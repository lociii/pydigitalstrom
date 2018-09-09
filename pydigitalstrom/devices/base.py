# -*- coding: UTF-8 -*-
from pydigitalstrom.client import DSClient
from pydigitalstrom.exceptions import DSCommandFailedException


class DSDevice(object):
    def __init__(self, client: DSClient, *args, **kwargs):
        self._client = client

    def request(self, url, **kwargs):
        url = url.format(**kwargs)
        json = self._client.request(url)
        if 'ok' not in json or not json['ok']:
            message = 'client raised an error while executing command'
            if 'message' in json:
                message += ': ' + json['message']
            raise DSCommandFailedException(message)

        if 'result' in json:
            return json['result']
        return True


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

    def request(self, url: str, **kwargs):
        kwargs.update(dict(id=self._id))
        super().request(url=url, **kwargs)
