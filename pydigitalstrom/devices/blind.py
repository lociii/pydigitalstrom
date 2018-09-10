# -*- coding: UTF-8 -*-
from pydigitalstrom.devices.base import DSTerminal
from pydigitalstrom.exceptions import DSParameterException


class DSBlind(DSTerminal):
    URL_UPDATE = '/json/device/getOutputValue?dsid={id}&offset=0'
    URL_ACTION_STOP = '/json/device/callScene?dsid={id}&sceneNumber=15'
    URL_ACTION_UP = '/json/device/callScene?dsid={id}&sceneNumber=14'
    URL_ACTION_DOWN = '/json/device/callScene?dsid={id}&sceneNumber=13'
    URL_SET_POSITION = '/json/device/setValue?dsid={id}&value={position}'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._position = 0

    def get_position(self):
        return self._position

    def set_position(self, position: int):
        if position < 0 or position > 255:
            raise DSParameterException('blind position must be an integer between 0 and 255')

        self.request(url=self.URL_SET_POSITION, position=position)
        self._position = position

    def stop(self):
        self.request(url=self.URL_ACTION_STOP, check_result=False)

    def move_up(self):
        self.request(url=self.URL_ACTION_UP, check_result=False)

    def move_down(self):
        self.request(url=self.URL_ACTION_DOWN, check_result=False)

    def update(self):
        self._position = self.request(url=self.URL_UPDATE)['value']
