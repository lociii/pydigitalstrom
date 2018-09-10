# -*- coding: UTF-8 -*-
from pydigitalstrom.devices.base import DSTerminal


class DSSwitchSensor(DSTerminal):
    URL_UPDATE = '/json/device/getOutputValue?dsid={id}&offset=0'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = self._data['on']

    def is_on(self):
        return self._state

    def update(self):
        json = self.request(self.URL_UPDATE)
        self._state = json['value'] > 0


class DSSwitch(DSSwitchSensor):
    URL_TURN_ON = '/json/device/turnOn?dsid={id}'
    URL_TURN_OFF = '/json/device/turnOff?dsid={id}'

    def turn_on(self):
        self.request(self.URL_TURN_ON, check_result=False)
        self._state = True

    def turn_off(self):
        self.request(self.URL_TURN_OFF, check_result=False)
        self._state = False

    def toggle(self):
        if self._state:
            self.turn_off()
        else:
            self.turn_on()
