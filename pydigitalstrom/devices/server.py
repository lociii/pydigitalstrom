# -*- coding: UTF-8 -*-
from pydigitalstrom.client import DSClient
from pydigitalstrom.devices.base import DSDevice


class DSServer(DSDevice):
    def __init__(self, client: DSClient, data: dict, *args, **kwargs):
        super().__init__(client=client, *args, **kwargs)
        self._data = data

    def get_data(self):
        """
        get server meta data

        :return: server meta data
        :rtype: dict
        """
        return self._data

    def update(self):
        """
        update server meta data
        """
        self._data = self.request(url=self._client.URL_SYSTEM_INFO)
