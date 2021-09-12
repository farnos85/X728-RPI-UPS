from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.components.sensor import (
                                                DEVICE_CLASS_VOLTAGE,
                                                DEVICE_CLASS_BATTERY,
                                                SCAN_INTERVAL
                                                )

import logging
import struct
import sys
import time
from smbus2 import SMBus

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    bus = SMBus(1)
    voltage = x728ups_voltage(bus)
    capacity = x728ups_capacity(bus)
    entities = [voltage, capacity]
    add_entities(entities, True)

class x728ups_voltage(Entity):
    def __init__(self, bus):
        self.address = 0x36
        self.bus = bus
        self._state = None
        #self.update()

    @property
    def name(self):
        return "X728UPS Voltage"
    
    @property
    def state(self):
        return round(self._state, 2)

    @property
    def unit_of_measurement(self):
        return "V"
    
    @property
    def is_on(self):
        return True

    @property
    def device_class(self):
        return DEVICE_CLASS_VOLTAGE

    @property
    def unique_id(self):
        return "X728upsV12345"

    @property
    def icon(self):
        return "mdi:flash"
    
    def update(self):
        _bus = self.bus
        try:
            read = _bus.read_word_data(self.address, 2)
            swapped = struct.unpack("<H", struct.pack(">H", read))[0]
        except:
            _LOGGER.error("Unable to access SMBUS")
        else:
            self._state = swapped * 1.23 /1000/16

class x728ups_capacity(Entity):
    def __init__(self, bus):
        self.address = 0x36
        self.bus = bus
        self._state = None
        #self.update()

    @property
    def name(self):
        return "X728UPS Battery level"
    
    @property
    def state(self):
        return round(self._state, 2)

    @property
    def unit_of_measurement(self):
        return "%"
    
    @property
    def is_on(self):
        return True

    @property
    def device_class(self):
        return DEVICE_CLASS_BATTERY

    @property
    def unique_id(self):
        return "X728upsB12345"

    @property
    def icon(self):
        return self._icon()
    
    def update(self):
        _bus = self.bus
        try:
            read = _bus.read_word_data(self.address, 4)
            swapped = struct.unpack("<H", struct.pack(">H", read))[0]
        except:
            _LOGGER.error("Unable to access SMBUS")
        else:
            self._state = swapped/256
    
    def _icon(self):
        cap = float(self._state)
        charge = ""
        if cap < 30:
            icon = f"mdi:battery{charge}-low"
        elif (cap >= 30) and (cap < 60):
            icon = f"mdi:battery{charge}-medium"
        elif (cap >= 60) and (cap < 90):
            icon = f"mdi:battery{charge}-high"
        else:
            icon = "mdi:battery"
        return icon