import json

import aiohttp

from pydigitalstrom.exceptions import DSCommandFailedException, DSRequestException


class DSRequestHandler:
    def __init__(self, host: str) -> None:
        self.host = host

    async def raw_request(self, url: str, **kwargs) -> str:
        """
        run a raw request against the digitalstrom server

        :param str url: URL path to request
        :param dict kwargs: kwargs to be forwarded to aiohttp.get
        :return: json response
        :rtype: dict
        :raises: DSRequestException
        :raises: DSCommandFailedException
        """
        url = "{host}{path}".format(host=self.host, path=url)

        # disable ssl verification for most servers miss valid certificates
        async with await self.get_aiohttp_session() as session:
            try:
                async with session.get(url=url, **kwargs) as response:
                    # check for server errors
                    if not response.status == 200:
                        raise DSRequestException(response.text)

                    try:
                        data = await response.json()
                    except json.decoder.JSONDecodeError:
                        raise DSRequestException("failed to json decode response")
                    if "ok" not in data or not data["ok"]:
                        raise DSCommandFailedException()
                    return data
            except aiohttp.ClientError:
                raise DSRequestException("request failed")

    async def get_aiohttp_session(self) -> aiohttp.client.ClientSession:
        """
        turn off ssl verification since most digitalstrom servers use
        self-signed certificates

        :return aiohttp client session
        :rtype: aiohttp.client.ClientSession
        """
        return aiohttp.client.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False)
        )
