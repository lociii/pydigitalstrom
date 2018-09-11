# -*- coding: UTF-8 -*-
from pydigitalstrom.client import DSClient
from pydigitalstrom.devices.base import DSDevice


class DSScene(DSDevice):
    URL_TURN_ON = '/json/zone/callScene?id={zone_id}&sceneNumber={scene_id}'
    URL_TURN_OFF = '/json/zone/undoScene?id={zone_id}&sceneNumber={scene_id}'

    def __init__(self, client: DSClient, data, *args, **kwargs):
        data['id'] = '{zone_id}.{scene_id}'.format(
            zone_id=data['zone_id'], scene_id=data['scene_id'])
        data['name'] = '{zone} / {name}'.format(
            zone=data['zone_name'], name=data['scene_name'])
        super().__init__(client=client, data=data, *args, **kwargs)

    async def turn_on(self):
        await self.request(url=self.URL_TURN_ON.format(
            zone_id=self._data['zone_id'], scene_id=self._data['scene_id']),
            check_result=False)

    async def turn_off(self):
        await self.request(url=self.URL_TURN_OFF.format(
            zone_id=self._data['zone_id'], scene_id=self._data['scene_id']),
            check_result=False)
