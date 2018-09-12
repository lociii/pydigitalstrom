# -*- coding: UTF-8 -*-
from pydigitalstrom.devices.base import DSDevice
from pydigitalstrom.exceptions import DSParameterException


class DSBlind(DSDevice):
    URL_UPDATE = '/json/device/getOutputValue?dsid={id}&offset=0'
    # scene 15 => stop
    URL_ACTION_STOP = '/json/device/callScene?dsid={id}&sceneNumber=15'
    # scene 14 => max
    URL_ACTION_UP = '/json/device/callScene?dsid={id}&sceneNumber=14'
    # scene 13 => min
    URL_ACTION_DOWN = '/json/device/callScene?dsid={id}&sceneNumber=13'
    URL_SET_POSITION = '/json/device/setValue?dsid={id}&value={position}'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._position = 0

    def get_position(self):
        return self._position

    async def set_position(self, position: int):
        if position < 0 or position > 255:
            raise DSParameterException(
                'blind position must be an integer between 0 and 255')

        await self.request(url=self.URL_SET_POSITION, position=position,
                           check_result=False)
        self._position = position

    async def stop(self):
        await self.request(url=self.URL_ACTION_STOP, check_result=False)

    async def move_up(self):
        await self.request(url=self.URL_ACTION_UP, check_result=False)

    async def move_down(self):
        await self.request(url=self.URL_ACTION_DOWN, check_result=False)

    async def update(self):
        data = await self.request(url=self.URL_UPDATE)
        self._position = data['value']
