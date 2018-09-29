# -*- coding: UTF-8 -*-
from pydigitalstrom.client import DSClient
from pydigitalstrom.devices.base import DSDevice


class DSAreaBlind(DSDevice):
    URL_CALL_SCENE = '/json/zone/callScene?id={zone}&groupID=2&' \
                     'sceneNumber={scene}&force=true'

    def __init__(self, client: DSClient, data,  *args, **kwargs):
        super().__init__(client, data, *args, **kwargs)
        self._is_closed = None
        self._update_callbacks = []

        # generate device name
        self._data['name'] = self._data['zone_name']
        if self._data['area_id'] > 0:
            area_name = self._data['area_name'] or 'Area {area}'.format(
                area=self._data['area_id'])
            self._data['name'] = '{name} - {area}'.format(
                name=self._data['name'], area=area_name)

    async def set_is_closed(self, is_closed):
        self._is_closed = is_closed
        await self.publish_update()

    async def publish_update(self):
        for callback in self._update_callbacks:
            await callback()

    def is_closed(self):
        return self._is_closed

    async def open(self):
        await self.request(url=self.URL_CALL_SCENE, check_result=False,
                           zone=self._data['zone_id'],
                           scene=self._data['area_id'] + 5)
        self._is_closed = False

    async def close(self):
        await self.request(url=self.URL_CALL_SCENE, check_result=False,
                           zone=self._data['zone_id'],
                           scene=self._data['area_id'])
        self._is_closed = True

    def register_update_callback(self, callback):
        self._update_callbacks.append(callback)
