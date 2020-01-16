import json

import aiohttp
import socket

from pydigitalstrom.exceptions import DSCommandFailedException, DSRequestException


class DSRequestHandler:
    def __init__(self, host: str, port: str) -> None:
        self.host = host
        self.port = port

    async def raw_request(self, url: str, **kwargs) -> str:
        """
        run a raw request against the digitalstrom server

        :param url: URL path to request
        :param kwargs: kwargs to be forwarded to aiohttp.get
        :return: json response
        :raises: DSRequestException
        :raises: DSCommandFailedException
        """
        url = f"https://{self.host}:{self.port}{url}"

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

    async def get_aiohttp_session(
        self, cookies: dict = None
    ) -> aiohttp.client.ClientSession:
        """
        turn off ssl verification since most digitalstrom servers use
        self-signed certificates

        :param cookies: a dict of cookies to set on the connection
        :return the initialized aiohttp client session
        """
        return aiohttp.client.ClientSession(
            connector=aiohttp.TCPConnector(family=socket.AF_INET, ssl=False),
            cookies=cookies,
        )
