from pydigitalstrom.client import DSClient


class DSDevice(object):
    ID_FIELD = "id"

    def __init__(self, client: DSClient, device_id, device_name, *args, **kwargs):
        self._client = client
        self._id = device_id
        self._name = device_name

    def __str__(self):
        return '<{type} {id} "{name}">'.format(
            type=self.__class__.__name__, id=self.unique_id, name=self.name
        )

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._id

    async def request(self, url: str, **kwargs):
        await self._client.stack.append(url=url.format(**kwargs))
