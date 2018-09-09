# -*- coding: UTF-8 -*-
from pydigitalstrom.devices.base import DSTerminal
from pydigitalstrom.exceptions import DSUnsupportedException


class DSLight(DSTerminal):
    URL_IDENTIFY = '/json/device/blink?dsid={id}'
    URL_UPDATE = '/json/device/getOutputValue?dsid={id}&offset=0'
    URL_TURN_ON = '/json/device/turnOn?dsid={id}'
    URL_TURN_OFF = '/json/device/turnOff?dsid={id}'
    URL_SET_BRIGHTNESS = '/device/setValue?dsid={id}&value={brightness}'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._brightness = None
        self._state = self._data['on']
        self._is_dimmable = False

        # large light devices cannot dim / mode 16 is switched output
        if self._data['hwFunction'] != 'KL' and self._data['outputMode'] != 16:
            self._is_dimmable = True

    def is_on(self):
        return self._state

    def get_brightness(self):
        return self._brightness

    def is_dimmable(self):
        return self._is_dimmable

    def identify(self):
        self.request(self.URL_IDENTIFY)

    def turn_on(self, **kwargs):
        brightness = kwargs.get('brightness', None)
        if not self.is_dimmable() and brightness:
            raise DSUnsupportedException('device does not support setting a brightness')

        if brightness:
            self.request(self.URL_SET_BRIGHTNESS, brightness=brightness)
            self._brightness = brightness
        else:
            self.request(self.URL_TURN_ON)

        self._state = True

    def turn_off(self):
        self.request(self.URL_TURN_OFF)
        self._state = False

    def toggle(self):
        if self._state:
            self.turn_off()
        else:
            self.turn_on()

    def update(self):
        json = self.request(self.URL_UPDATE)
        self._state = json['value'] > 0
        self._brightness = json['value']
