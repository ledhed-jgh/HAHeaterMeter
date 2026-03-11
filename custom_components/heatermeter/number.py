import logging
from homeassistant.components.number import NumberEntity, NumberDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfTemperature, CONF_HOST, CONF_PORT
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up HeaterMeter number entities from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    
    entities = [HeaterMeterNumber(coordinator, entry, "setpoint", "Setpoint", None)]
    for i in range(4):
        entities.append(HeaterMeterNumber(coordinator, entry, "hi", "Alarm High", i))
        entities.append(HeaterMeterNumber(coordinator, entry, "lo", "Alarm Low", i))
    
    async_add_entities(entities)

class HeaterMeterNumber(CoordinatorEntity, NumberEntity):
    _attr_has_entity_name = False 

    def __init__(self, coordinator, entry, control_type, label, probe_idx=None):
        super().__init__(coordinator)
        self._entry, self._type, self._label, self._probe_idx = entry, control_type, label, probe_idx
        self._attr_device_class = NumberDeviceClass.TEMPERATURE
        self._attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT
        self._attr_native_step, self._attr_native_min_value, self._attr_native_max_value = 1, -1000, 1000
        
        suffix = f"probe{probe_idx}" if isinstance(probe_idx, int) else "system"
        self._attr_unique_id = f"{entry.entry_id}_{suffix}_{control_type}"
        
        if isinstance(probe_idx, int):
            self.entity_id = f"number.{DOMAIN}_probe{probe_idx}_{control_type}"
        else:
            self.entity_id = f"number.{DOMAIN}_{control_type}"

    @property
    def name(self):
        if isinstance(self._probe_idx, int) and self.coordinator.data:
            temps = self.coordinator.data.get("temps", [])
            if len(temps) > self._probe_idx:
                p_name = temps[self._probe_idx].get("n")
                if p_name: return f"{p_name} {self._label}"
        prefix = "Pit" if self._probe_idx == 0 else f"Probe {self._probe_idx}" if isinstance(self._probe_idx, int) else "HeaterMeter"
        return f"{prefix} {self._label}"

    @property
    def native_value(self):
        data_store = self.hass.data[DOMAIN][self._entry.entry_id]
        if isinstance(self._probe_idx, int) and self._type != "setpoint":
            idx = (self._probe_idx * 2) + (1 if self._type == "hi" else 0)
            if idx in data_store.get("pending_alarms", {}): return data_store["pending_alarms"][idx]
        if not self.coordinator.data: return None
        if self._type == "setpoint": return self.coordinator.data.get("set")
        temps = self.coordinator.data.get("temps", [])
        if len(temps) > self._probe_idx:
            return temps[self._probe_idx].get("a", {}).get("h" if self._type == "hi" else "l")
        return None

    async def async_set_native_value(self, value: float):
        """Update the setting via the correct service."""
        val = int(value)
        if self._type == "setpoint":
            await self.hass.services.async_call(
                DOMAIN, 
                "new_setpoint",
                {"temperature": val}, 
                blocking=True
            )
        else:
            idx = (self._probe_idx * 2) + (1 if self._type == "hi" else 0)
            await self.hass.services.async_call(
                DOMAIN, 
                "set_alarm_by_index", 
                {"index": idx, "value": val}, 
                blocking=True
            )

    @property
    def device_info(self):
        v = self.hass.data[DOMAIN][self._entry.entry_id].get("sw_version", "Unknown")
        return {"identifiers": {(DOMAIN, self._entry.entry_id)}, "name": "HeaterMeter BBQ", "sw_version": v}