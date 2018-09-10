# -*- coding: UTF-8 -*-
from pydigitalstrom.client import DSClient
from pydigitalstrom.devices.base import DSDevice


class DSScene(DSDevice):
    URL_TURN_ON = '/json/zone/callScene?id={zone_id}&sceneNumber={scene_id}'
    URL_TURN_OFF = '/json/zone/undoScene?id={zone_id}&sceneNumber={scene_id}'

    def __init__(self, client: DSClient, data, *args, **kwargs):
        super().__init__(client=client, *args, **kwargs)
        self._data = data

    @property
    def name(self):
        return '{zone} / {name}'.format(
            zone=self._data['zone_name'], name=self._data['name'])

    @property
    def unique_id(self):
        return '{zone_id}.{scene_id}'.format(
            zone_id=self._data['zone_id'], scene_id=self._data['scene_id'])

    def turn_on(self):
        self.request(url=self.URL_TURN_ON.format(
            zone_id=self._data['zone_id'], scene_id=self._data['scene_id']), check_result=False)

    def turn_off(self):
        self.request(url=self.URL_TURN_OFF.format(
            zone_id=self._data['zone_id'], scene_id=self._data['scene_id']), check_result=False)
