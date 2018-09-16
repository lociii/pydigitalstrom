# -*- coding: UTF-8 -*-
from pydigitalstrom.client import DSClient
from pydigitalstrom.devices.base import DSDevice


class DSAreaLight(DSDevice):
    URL_CALL_SCENE = '/json/zone/callScene?id={zone}&groupID=1&' \
                     'sceneNumber={scene}&force=true'

    def __init__(self, client: DSClient, data,  *args, **kwargs):
        super().__init__(client, data, *args, **kwargs)
        self._state = None
        self._update_callbacks = []

        # generate device name
        self._data['name'] = self._data['zone_name']
        if self._data['area_id'] > 0:
            area_name = self._data['area_name'] or 'Area {area}'.format(
                area=self._data['area_id'])
            self._data['name'] = '{name} - {area}'.format(
                name=self._data['name'], area=area_name)

    async def set_state(self, state):
        self._state = state
        await self.publish_update()

    async def publish_update(self):
        for callback in self._update_callbacks:
            await callback()

    def is_on(self):
        return self._state

    async def turn_on(self):
        await self.request(url=self.URL_CALL_SCENE, check_result=False,
                           zone=self._data['zone_id'],
                           scene=self._data['area_id'] + 5)
        self._state = True

    async def turn_off(self):
        await self.request(url=self.URL_CALL_SCENE, check_result=False,
                           zone=self._data['zone_id'],
                           scene=self._data['area_id'])
        self._state = False

    async def toggle(self):
        if self._state is True:
            await self.turn_off()
        elif self._state is False:
            await self.turn_on()

    def register_update_callback(self, callback):
        self._update_callbacks.append(callback)
