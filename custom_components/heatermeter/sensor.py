from homeassistant.components.sensor import (
    SensorEntity, 
    SensorDeviceClass, 
    SensorStateClass
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import (
    UnitOfTemperature, 
    CONF_HOST, 
    CONF_PORT
)
from . import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    
    entities = [
        HeaterMeterSensor(coordinator, entry, 'fan', 'Fan Speed', 'mdi:fan', '%', None),
    ]
    
    for i in range(4):
        entities.append(
            HeaterMeterSensor(coordinator, entry, 'temp', 'Temperature', SensorDeviceClass.TEMPERATURE, None, i)
        )
        
    async_add_entities(entities)

class HeaterMeterSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = False 

    def __init__(self, coordinator, entry, sensor_type, label, icon_or_class, unit=None, probe_idx=None):
        super().__init__(coordinator)
        self._entry, self._type, self._label, self._probe_idx = entry, sensor_type, label, probe_idx
        
        if isinstance(icon_or_class, SensorDeviceClass):
            self._attr_device_class = icon_or_class
        else:
            self._attr_icon = icon_or_class
            self._attr_device_class = None

        self._attr_native_unit_of_measurement = unit or (UnitOfTemperature.FAHRENHEIT if self._attr_device_class == SensorDeviceClass.TEMPERATURE else None)
        self._attr_state_class = SensorStateClass.MEASUREMENT

        suffix = f"probe{probe_idx}" if isinstance(probe_idx, int) else "system"
        self._attr_unique_id = f"{entry.entry_id}_{suffix}_{sensor_type}"

        if isinstance(probe_idx, int):
            self.entity_id = f"sensor.{DOMAIN}_probe{probe_idx}_{sensor_type}"
        else:
            self.entity_id = f"sensor.{DOMAIN}_{sensor_type}"

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
        if not self.coordinator.data: return None
        d = self.coordinator.data
        if self._type == 'fan': return d.get("fan", {}).get("c")
        if self._type == 'temp' and isinstance(self._probe_idx, int):
            temps = d.get("temps", [])
            if len(temps) > self._probe_idx: return temps[self._probe_idx].get("c")
        return None

    @property
    def device_info(self):
        v = self.hass.data[DOMAIN][self._entry.entry_id].get("sw_version", "Unknown")
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "HeaterMeter BBQ",
            "manufacturer": "CapnBry",
            "model": "HeaterMeter v4.x",
            "sw_version": v,
            "configuration_url": f"http://{self._entry.data.get(CONF_HOST)}:{self._entry.data.get(CONF_PORT, 80)}",
        }