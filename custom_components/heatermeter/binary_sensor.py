import logging
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import CONF_HOST, CONF_PORT
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    async_add_entities([
        HeaterMeterBinarySensor(coordinator, entry, "alarm", "Alarm", BinarySensorDeviceClass.PROBLEM),
        HeaterMeterBinarySensor(coordinator, entry, "lid", "Lid", BinarySensorDeviceClass.OPENING)
    ])

class HeaterMeterBinarySensor(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = False

    def __init__(self, coordinator, entry, sensor_type, label, device_class):
        super().__init__(coordinator)
        self._entry, self._type, self._label = entry, sensor_type, label
        self._attr_device_class = device_class
        self._attr_unique_id = f"{entry.entry_id}_system_{sensor_type}"
        self.entity_id = f"binary_sensor.{DOMAIN}_{sensor_type}"

    @property
    def name(self): return self._label

    @property
    def is_on(self):
        if not self.coordinator.data: return False
        if self._type == "alarm":
            return any(p.get("a", {}).get("r") in ["H", "L"] for p in self.coordinator.data.get("temps", []))
        return self.coordinator.data.get("lid", 0) > 0

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data: return None
        if self._type == "alarm":
            mapping = {"H": "High", "L": "Low"}
            for probe in self.coordinator.data.get("temps", []):
                r = probe.get("a", {}).get("r")
                if r in mapping:
                    return {"alarm_type": mapping[r], "probe_name": probe.get("n", "Unknown")}
        return {"seconds_remaining": self.coordinator.data.get("lid", 0)} if self._type == "lid" else None

    @property
    def device_info(self):
        v = self.hass.data[DOMAIN][self._entry.entry_id].get("sw_version", "Unknown")
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "HeaterMeter BBQ",
            "sw_version": v,
        }