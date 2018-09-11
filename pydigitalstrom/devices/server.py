# -*- coding: UTF-8 -*-
from pydigitalstrom.client import DSClient
from pydigitalstrom.devices.base import DSDevice


class DSServer(DSDevice):
    URL_SYSTEM_INFO = '/json/system/version'

    def __init__(self, client: DSClient, data: dict, *args, **kwargs):
        data['id'] = data['MachineID']
        data['name'] = 'Server'
        super().__init__(client=client, data=data, *args, **kwargs)

    def get_data(self):
        """
        get server meta data

        :return: server meta data
        :rtype: dict
        """
        return self._data

    async def update(self):
        """
        update server meta data
        """
        data = await self.request(url=self.URL_SYSTEM_INFO)
        self._data.update(data)
        self._data['id'] = self._data['MachineID']
