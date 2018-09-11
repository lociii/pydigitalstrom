# -*- coding: UTF-8 -*-
from pydigitalstrom.client import DSClient


class DSDevice(object):
    ID_FIELD = 'id'

    def __init__(self, client: DSClient, data: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client = client
        self._id = data[self.ID_FIELD]
        self._data = data

    def __str__(self):
        return '<{type} {id} "{name}">'.format(
            type=self.__class__.__name__, id=self.unique_id,
            name=self.name)

    def get_data(self):
        return self._data

    @property
    def name(self):
        return self._data['name']

    @property
    def unique_id(self):
        return self._id

    async def request(self, url: str, check_result=True, **kwargs):
        kwargs.update(self._data)
        return await self._client.request(
            url=url.format(**kwargs), check_result=check_result)
