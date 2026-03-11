import voluptuous as vol
import logging
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import (
    CONF_HOST, 
    CONF_PORT, 
    CONF_API_KEY, 
    CONF_SCAN_INTERVAL
)
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)
DEFAULT_INTERVAL = 5

class HeaterMeterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HeaterMeter."""
    VERSION = 1

    def __init__(self):
        self._discovered_info = {}
        self._reconfig_entry = None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return HeaterMeterOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            url = f"http://{user_input[CONF_HOST]}:{user_input[CONF_PORT]}/luci/lm/hmstatus"
            try:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        if self._reconfig_entry:
                            return self.async_update_reload_and_abort(
                                self._reconfig_entry, 
                                data=user_input
                            )
                        
                        # Set unique ID to prevent duplicates
                        await self.async_set_unique_id(user_input[CONF_HOST])
                        self._abort_if_unique_id_configured()
                        
                        return self.async_create_entry(
                            title=f"HeaterMeter ({user_input[CONF_HOST]})", 
                            data=user_input
                        )
                    errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "cannot_connect"

        # Default values for the form
        d_host = self._discovered_info.get(CONF_HOST, "")
        d_port = self._discovered_info.get(CONF_PORT, 80)
        
        if self._reconfig_entry:
            d_host = self._reconfig_entry.data.get(CONF_HOST)
            d_port = self._reconfig_entry.data.get(CONF_PORT)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST, default=d_host): str,
                vol.Required(CONF_PORT, default=d_port): int,
                vol.Required(CONF_API_KEY): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                ),
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_INTERVAL): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1, max=60, step=1, mode=selector.NumberSelectorMode.BOX
                    )
                ),
            }),
            errors=errors,
        )

    async def async_step_zeroconf(self, discovery_info: ZeroconfServiceInfo):
        """Handle zeroconf discovery."""
        host = discovery_info.host
        port = discovery_info.port or 80
        hostname = discovery_info.hostname.replace(".local.", "")

        _LOGGER.debug("HeaterMeter discovery found: %s at %s", hostname, host)

        # Use hostname for a stable unique ID
        await self.async_set_unique_id(hostname)
        self._abort_if_unique_id_configured(updates={CONF_HOST: host})

        self._discovered_info = {
            CONF_HOST: host,
            CONF_PORT: port,
        }

        self.context.update({
            "title_placeholders": {"name": "HeaterMeter BBQ"}
        })

        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(self, user_input=None):
        """Confirm discovery and get the API Key."""
        errors = {}
        if user_input is not None:
            # Merge discovery data with user-provided API key
            complete_input = {**self._discovered_info, **user_input}
            # Add default scan interval if not in discovery
            complete_input.setdefault(CONF_SCAN_INTERVAL, DEFAULT_INTERVAL)
            
            return self.async_create_entry(
                title="HeaterMeter BBQ",
                data=complete_input
            )

        return self.async_show_form(
            step_id="discovery_confirm",
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                ),
            }),
            description_placeholders={"host": self._discovered_info[CONF_HOST]},
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input=None):
        """Handle reconfiguration of an existing entry."""
        self._reconfig_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_user()

class HeaterMeterOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, 
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_INTERVAL)
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(CONF_SCAN_INTERVAL, default=current_interval): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1, max=60, step=1, mode=selector.NumberSelectorMode.BOX
                    )
                ),
            }),
        )