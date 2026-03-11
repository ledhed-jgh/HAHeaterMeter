import logging
import asyncio
import voluptuous as vol
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import (
    CONF_HOST, 
    CONF_PORT, 
    CONF_API_KEY, 
    CONF_SCAN_INTERVAL,
    Platform
)

DOMAIN = "heatermeter"
PLATFORMS = [Platform.SENSOR, Platform.NUMBER, Platform.BINARY_SENSOR]
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HeaterMeter from a config entry."""
    conf = entry.data
    session = async_get_clientsession(hass)

    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, conf.get(CONF_SCAN_INTERVAL, 5))

    async def async_update_data():
        """Fetch data from HeaterMeter status JSON."""
        url = f"http://{conf[CONF_HOST]}:{conf[CONF_PORT]}/luci/lm/hmstatus"
        async with session.get(url, timeout=5) as response:
            if response.status != 200:
                raise Exception(f"Error communicating with HeaterMeter: {response.status}")
            return await response.json()

    coordinator = DataUpdateCoordinator(
        hass, 
        _LOGGER, 
        name="heatermeter_coordinator",
        update_method=async_update_data,
        update_interval=timedelta(seconds=scan_interval),
    )

    sw_version = "Unknown"
    v_url = f"http://{conf[CONF_HOST]}:{conf[CONF_PORT]}/luci/lm/api/version"
    try:
        async with session.get(v_url, timeout=5) as resp:
            if resp.status == 200:
                v_json = await resp.json()
                sw_version = str(v_json.get("ucid", "Unknown"))
    except Exception: 
        _LOGGER.debug("HeaterMeter: Could not fetch version info")

    hass.data.setdefault(DOMAIN, {})
    data_store = {
        "coordinator": coordinator,
        "pending_alarms": {},
        "alarm_timer": None,
        "sw_version": sw_version
    }
    hass.data[DOMAIN][entry.entry_id] = data_store

    await coordinator.async_config_entry_first_refresh()

    async def send_api_command(params):
        """Unified POST command using Form-Encoded data."""
        url = f"http://{conf[CONF_HOST]}:{conf[CONF_PORT]}/luci/lm/api/config"
        payload = {**params, "apikey": conf[CONF_API_KEY]}
        
        _LOGGER.debug("HeaterMeter: Attempting POST to %s with payload: %s", url, params)
        
        try:
            async with session.post(url, data=payload, timeout=10) as response:
                response_text = await response.text()
                if response.status == 200:
                    _LOGGER.info("HeaterMeter: Command accepted. Response: %s", response_text)
                    return True
                _LOGGER.error("HeaterMeter: API Error (Status %s): %s", response.status, response_text)
                return False
        except Exception as e:
            _LOGGER.error("HeaterMeter: Connection error during API call: %s", e)
            return False

    async def new_setpoint_temperature(call):
        """Service handler for the main Setpoint (sp)."""
        _LOGGER.info("HeaterMeter: new_setpoint service called with %s", call.data)
        
        temp = call.data.get("temperature")
        if temp is not None:
            target_val = str(int(float(temp)))
            if await send_api_command({"sp": target_val}):
                await asyncio.sleep(1.5)
                await coordinator.async_request_refresh()

    async def handle_set_alarms(call):
        """Backwards compatibility: Sets all 8 alarms at once."""
        _LOGGER.info("HeaterMeter: handle_set_alarms legacy service called")
        alarm_csv = call.data.get("alarms")
        if alarm_csv and await send_api_command({"al": alarm_csv}):
            await asyncio.sleep(2.0)
            await coordinator.async_request_refresh()

    async def handle_set_alarm_by_index(call):
        """Debounced handler for single index updates."""
        idx, val = call.data.get("index"), call.data.get("value")
        if idx is None or val is None: return

        data_store["pending_alarms"][idx] = val
        if data_store["alarm_timer"]:
            data_store["alarm_timer"].cancel()

        async def debounced_send():
            await asyncio.sleep(1.5)
            if not coordinator.data: return
            
            alarms = []
            for t in coordinator.data.get("temps", []):
                alarms.append(str(t.get("a", {}).get("l", -1000)))
                alarms.append(str(t.get("a", {}).get("h", 1000)))

            for p_idx, p_val in data_store["pending_alarms"].items():
                if p_idx < len(alarms):
                    alarms[p_idx] = str(p_val)

            alarm_csv = ",".join(alarms)
            if await send_api_command({"al": alarm_csv}):
                data_store["pending_alarms"].clear()
                await asyncio.sleep(2.0)
                await coordinator.async_request_refresh()
            data_store["alarm_timer"] = None

        data_store["alarm_timer"] = hass.async_create_task(debounced_send())

    hass.services.async_register(
        DOMAIN, "new_setpoint", new_setpoint_temperature,
        schema=vol.Schema({vol.Required("temperature"): vol.Coerce(int)})
    )
    hass.services.async_register(
        DOMAIN, "set_alarms", handle_set_alarms,
        schema=vol.Schema({vol.Required("alarms"): str})
    )
    hass.services.async_register(
        DOMAIN, "set_alarm_by_index", handle_set_alarm_by_index,
        schema=vol.Schema({
            vol.Required("index"): vol.Coerce(int),
            vol.Required("value"): vol.Coerce(int)
        })
    )

    entry.async_on_unload(entry.add_update_listener(update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok