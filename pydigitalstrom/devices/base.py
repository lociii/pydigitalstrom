# -*- coding: UTF-8 -*-
from pydigitalstrom.client import DSClient


class DSDevice(object):
    def __init__(self, client: DSClient, *args, **kwargs):
        self._client = client

    def request(self, url, check_result=True, **kwargs):
        return self._client.request(
            url=url.format(**kwargs), check_result=check_result)


class DSTerminal(DSDevice):
    def __init__(self, client: DSClient, data: dict, *args, **kwargs):
        super().__init__(client=client, *args, **kwargs)
        self._id = data['id']
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

    def request(self, url: str, check_result=True, **kwargs):
        kwargs.update(dict(id=self._id))
        return super().request(
            url=url, check_result=check_result, **kwargs)
