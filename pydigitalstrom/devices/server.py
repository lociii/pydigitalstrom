# -*- coding: UTF-8 -*-
from pydigitalstrom.client import DSClient
from pydigitalstrom.devices.base import DSDevice


class DSServer(DSDevice):
    URL_SYSTEM_INFO = '/json/system/version'

    def __init__(self, client: DSClient, data: dict, *args, **kwargs):
        super().__init__(client=client, *args, **kwargs)
        self._data = data

    @property
    def name(self):
        return 'server'

    @property
    def unique_id(self):
        return self._data['MachineID']

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
        self._data = self.request(url=self.URL_SYSTEM_INFO)
