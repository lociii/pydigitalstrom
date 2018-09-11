# -*- coding: UTF-8 -*-
from pydigitalstrom.devices.base import DSDevice


class DSSwitchSensor(DSDevice):
    URL_UPDATE = '/json/device/getOutputValue?dsid={id}&offset=0'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = self._data['on']

    def is_on(self):
        return self._state

    async def update(self):
        data = await self.request(url=self.URL_UPDATE)
        self._state = data['value'] > 0


class DSSwitch(DSSwitchSensor):
    URL_TURN_ON = '/json/device/turnOn?dsid={id}'
    URL_TURN_OFF = '/json/device/turnOff?dsid={id}'

    async def turn_on(self):
        await self.request(url=self.URL_TURN_ON, check_result=False)
        self._state = True

    async def turn_off(self):
        await self.request(url=self.URL_TURN_OFF, check_result=False)
        self._state = False

    async def toggle(self):
        if self._state:
            await self.turn_off()
        else:
            await self.turn_on()
