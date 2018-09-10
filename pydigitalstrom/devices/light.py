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
        self._state = self._data['on']
        self._brightness = None
        self._is_dimmable = False

        # large light devices cannot dim / mode 16 is switched output
        if 'hwFunction' in self._data and self._data['hwFunction'] != 'KL' and \
                'outputMode' in self._data and self._data['outputMode'] != 16:
            self._is_dimmable = True

        # device is off
        if self._is_dimmable and not self._state:
            self._brightness = 0

    def is_on(self):
        return self._state

    def get_brightness(self):
        return self._brightness

    def is_dimmable(self):
        return self._is_dimmable

    def identify(self):
        self.request(url=self.URL_IDENTIFY, check_result=False)

    def turn_on(self, **kwargs):
        brightness = kwargs.get('brightness', None)
        if not self.is_dimmable() and brightness:
            raise DSUnsupportedException('device does not support setting a brightness')

        if brightness:
            self.request(url=self.URL_SET_BRIGHTNESS, brightness=brightness, check_result=False)
            self._brightness = brightness
        else:
            self.request(url=self.URL_TURN_ON, check_result=False)
            if self._is_dimmable:
                self._brightness = 255

        self._state = True

    def turn_off(self):
        self.request(url=self.URL_TURN_OFF, check_result=False)
        self._state = False
        if self._is_dimmable:
            self._brightness = 0

    def toggle(self):
        if self._state:
            self.turn_off()
        else:
            self.turn_on()

    def update(self):
        data = self.request(url=self.URL_UPDATE)
        self._state = data['value'] > 0
        if self._is_dimmable:
            self._brightness = data['value']
