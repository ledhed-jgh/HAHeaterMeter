"""
Support for reading HeaterMeter data. See https://github.com/CapnBry/HeaterMeter/wiki/Accessing-Raw-Data-Remotely

"""
import logging
import requests
import json
from datetime import timedelta
import homeassistant.util.dt as dt_util
import voluptuous as vol

from homeassistant.helpers.config_validation import (  # noqa
    PLATFORM_SCHEMA, PLATFORM_SCHEMA_BASE)
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
        CONF_HOST, CONF_PORT, CONF_API_KEY, CONF_UNIT_SYSTEM, CONF_SCAN_INTERVAL, 
        CONF_RESOURCES, TEMP_CELSIUS, TEMP_FAHRENHEIT
    )
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

ENTITY_ID_FORMAT = DOMAIN + '.{}'

BASE_URL = 'http://{0}:{1}{2}'
SCAN_INTERVAL = timedelta(seconds=2)
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=1)

SENSOR_TYPES = {
    'setpoint': ['Setpoint', '', 'mdi:thermometer'],
    'lid': ['Lid', '', 'mdi:room-service'],
    'fan': ['Fan', '%', 'mdi:fan'],
    'alarm': ['Alarm', '', 'mdi:alert'],
    'probe0_temperature': ['Pit Temperature', '', 'mdi:thermometer'],
    'probe0_hi': ['Pit High', '', 'mdi:thermometer'],
    'probe0_lo': ['Pit Low', '', 'mdi:thermometer'],
    'probe1_temperature': ['Probe1 Temperature', '', 'mdi:thermometer'],
    'probe1_hi': ['Probe1 High', '', 'mdi:thermometer'],
    'probe1_lo': ['Probe1 Low', '', 'mdi:thermometer'],
    'probe2_temperature': ['Probe2 Temperature', '', 'mdi:thermometer'],
    'probe2_hi': ['Probe2 High', '', 'mdi:thermometer'],
    'probe2_lo': ['Probe2 Low', '', 'mdi:thermometer'],
    'probe3_temperature': ['Probe3 Temperature', '', 'mdi:thermometer'],
    'probe3_hi': ['Probe3 High', '', 'mdi:thermometer'],
    'probe3_lo': ['Probe3 Low', '', 'mdi:thermometer']
}

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the HeaterMeter sensors."""

    _LOGGER.debug("HeaterMeter: config = %s", config)
    _LOGGER.debug("HeaterMeter: hass.data = %s", hass.data[DOMAIN])
    _LOGGER.debug("HeaterMeter: hass = %s", hass)
    _LOGGER.debug("HeaterMeter: discovery_info = %s", discovery_info)
       
    host = hass.data[DOMAIN][CONF_HOST]
    port = hass.data[DOMAIN][CONF_PORT]

    # Default units to Celsius
    TEMP_UNITS = TEMP_CELSIUS

    # Unspecified Units default to HA system units
    if not hass.data[DOMAIN][CONF_UNIT_SYSTEM]:
        units = hass.config.units.name
    elif hass.data[DOMAIN][CONF_UNIT_SYSTEM].lower() == "auto":
        units = hass.config.units.name
    else:
        units = hass.data[DOMAIN][CONF_UNIT_SYSTEM]

    if units.lower() == "metric":
        TEMP_UNITS = TEMP_CELSIUS

    if units.lower() == "imperial":
        TEMP_UNITS = TEMP_FAHRENHEIT

    # Set Temperature Units based on global system settings
    SENSOR_TYPES['setpoint'][1]             = TEMP_UNITS
    SENSOR_TYPES['probe0_temperature'][1]   = TEMP_UNITS
    SENSOR_TYPES['probe0_hi'][1]            = TEMP_UNITS
    SENSOR_TYPES['probe0_lo'][1]            = TEMP_UNITS
    SENSOR_TYPES['probe1_temperature'][1]   = TEMP_UNITS
    SENSOR_TYPES['probe1_hi'][1]            = TEMP_UNITS
    SENSOR_TYPES['probe1_lo'][1]            = TEMP_UNITS
    SENSOR_TYPES['probe2_temperature'][1]   = TEMP_UNITS
    SENSOR_TYPES['probe2_hi'][1]            = TEMP_UNITS
    SENSOR_TYPES['probe2_lo'][1]            = TEMP_UNITS
    SENSOR_TYPES['probe3_temperature'][1]   = TEMP_UNITS
    SENSOR_TYPES['probe3_hi'][1]            = TEMP_UNITS
    SENSOR_TYPES['probe3_lo'][1]            = TEMP_UNITS

    try:
        data = HeaterMeterData(host, port)
    except RunTimeError:
        _LOGGER.error("HeaterMeter: Unable to connect fetch data from HeaterMeter %s:%s",
                      host, port)
        return False

    entities = []

    for resource in SENSOR_TYPES:
        sensor_type = resource.lower()
        entities.append(HeaterMeterSensor(data, sensor_type))
    
    _LOGGER.debug("HeaterMeter: entities = %s", entities)
    add_entities(entities)


# pylint: disable=abstract-method
class HeaterMeterData(object):
    """Representation of a HeaterMeter."""

    def __init__(self, host, port):
        """Initialize the HeaterMeter."""
        self._host = host
        self._port = port
        self.data = None
        self._backoff = dt_util.utcnow()

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Update the data from the HeaterMeter."""

        _LOGGER.debug("HeaterMeter: Backoff = %i", self._backoff - dt_util.utcnow())
        if self._backoff > dt_util.utcnow():
            return

        dataurl = BASE_URL.format(
                    self._host, self._port,
                    '/luci/lm/hmstatus'
        )   #new API /luci/lm/api/status
        try:
            response = requests.get(dataurl, timeout=5)
            self.data = response.json()
        except requests.exceptions.ConnectionError:
            _LOGGER.error("HeaterMeter: No route to device %s", dataurl)
            self.data = None
            self._backoff = dt_util.utcnow() + timedelta(seconds=60)
            
        _LOGGER.debug("HeaterMeter: Data = %s", self.data)


class HeaterMeterSensor(Entity):
    """Representation of a HeaterMeter sensor from the HeaterMeter."""

    def __init__(self, data, sensor_type):
        """Initialize the sensor."""
        self.data = data
        self.type = sensor_type
        self.entity_id = ENTITY_ID_FORMAT.format(sensor_type)
        self._name = SENSOR_TYPES[self.type][0]
        self._unit_of_measurement = SENSOR_TYPES[self.type][1]
        self._icon = SENSOR_TYPES[self.type][2]
        self._state = None
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    # @property
    # def state_attributes(self):
    # #def device_state_attributes(self):
    #     """Return the state attributes of the GPS."""
    #     return {
    #         ATTR_HI: "HI",
    #         ATTR_LO: "LO",
    #     }

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    def update(self):
        """Get the latest data and use it to update our sensor state."""
        self.data.update()
        #_LOGGER.debug("HeaterMeter: SensorData = %s", self.data.data)
        #_LOGGER.debug("HeaterMeter: type = %s", self.type)
        
        if self.data.data == None:
            self._state = "Unknown"
        else:
            if self.type == 'setpoint':
                self._state = self.data.data["set"]
            if self.type == 'fan':
                self._state = self.data.data["fan"]["c"]
            if self.type == 'lid':
                if self.data.data["lid"] == 0:
                    self._state =  "Closed"
                else:
                    self._state =  "Open"
            if self.type == 'alarm':
                if self.data.data["temps"][0]["a"]["r"] is not None:
                    self._state = "on"
                elif self.data.data["temps"][1]["a"]["r"] is not None:
                    self._state = "on"
                elif self.data.data["temps"][2]["a"]["r"] is not None:
                    self._state = "on"
                elif self.data.data["temps"][3]["a"]["r"] is not None:
                    self._state = "on"
                else:
                    self._state = "off"
            if self.type == 'probe0_temperature':
                self._state = self.data.data["temps"][0]["c"]
                self._name = self.data.data["temps"][0]["n"]
            if self.type == 'probe0_hi':
                P0HI = self.data.data["temps"][0]["a"]["h"]
                if P0HI > 0:
                    self._state = self.data.data["temps"][0]["a"]["h"]
                else:
                    self._state = "-"
                self._name = self.data.data["temps"][0]["n"] + " Alarm: High"
            if self.type == 'probe0_lo':
                P0LO = self.data.data["temps"][0]["a"]["l"]
                if P0LO > 0:
                    self._state = self.data.data["temps"][0]["a"]["l"]
                else:
                    self._state = "-"
                self._name = self.data.data["temps"][0]["n"] + " Alarm: Low"
            if self.type == 'probe1_temperature':
                self._state = self.data.data["temps"][1]["c"]
                self._name = self.data.data["temps"][1]["n"]
            if self.type == 'probe1_hi':
                P1HI = self.data.data["temps"][1]["a"]["h"]
                if P1HI > 0:
                    self._state = self.data.data["temps"][1]["a"]["h"]
                else:
                    self._state = "-"
                self._name = self.data.data["temps"][1]["n"] + " Alarm: High"
            if self.type == 'probe1_lo':
                P1LO = self.data.data["temps"][1]["a"]["l"]
                if P1LO > 0:
                    self._state = self.data.data["temps"][1]["a"]["l"]
                else:
                    self._state = "-"
                self._name = self.data.data["temps"][1]["n"] + " Alarm: Low"
            if self.type == 'probe2_temperature':
                self._state = self.data.data["temps"][2]["c"]
                self._name = self.data.data["temps"][2]["n"]
            if self.type == 'probe2_hi':
                P2HI = self.data.data["temps"][2]["a"]["h"]
                if P2HI > 0:
                    self._state = self.data.data["temps"][2]["a"]["h"]
                else:
                    self._state = "-"
                self._name = self.data.data["temps"][2]["n"] + " Alarm: High"
            if self.type == 'probe2_lo':
                P2LO = self.data.data["temps"][2]["a"]["l"]
                if P2LO > 0:
                    self._state = self.data.data["temps"][2]["a"]["l"]
                else:
                    self._state = "-"
                self._name = self.data.data["temps"][2]["n"] + " Alarm: Low"
            if self.type == 'probe3_temperature':
                self._state = self.data.data["temps"][3]["c"]
                self._name = self.data.data["temps"][3]["n"]
            if self.type == 'probe3_hi':
                P3HI = self.data.data["temps"][3]["a"]["h"]
                if P3HI > 0:
                    self._state = self.data.data["temps"][3]["a"]["h"]
                else:
                    self._state = "-"
                self._name = self.data.data["temps"][3]["n"] + " Alarm: High"
            if self.type == 'probe3_lo':
                P3LO = self.data.data["temps"][3]["a"]["l"]
                if P3LO > 0:
                    self._state = self.data.data["temps"][3]["a"]["l"]
                else:
                    self._state = "-"
                self._name = self.data.data["temps"][3]["n"] + " Alarm: Low"