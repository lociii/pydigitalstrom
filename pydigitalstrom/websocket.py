import aiohttp
import asyncio
import json
import time

from pydigitalstrom.client import DSClient
from pydigitalstrom.log import DSLog


class DSWebsocketEventListener:
    def __init__(self, client: DSClient, event_name: str):
        self._client = client
        self._event_name = event_name
        self._callbacks = []

        self._ws = None
        self._last_keepalive = None

    def register(self, callback: callable):
        self._callbacks.append(callback)

    async def _get_cookie(self):
        return dict(token=await self._client.get_session_token())

    async def start(self):
        session = await self._client.get_aiohttp_session(
            cookies=await self._get_cookie()
        )
        url = f"wss://{self._client.host}:{self._client.port}/websocket"
        self._ws = session.ws_connect(url=url)
        async with self._ws as ws:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await self._handle_event(event=json.loads(msg.data))
                else:
                    DSLog.logger.warn(f"DS websocket got unknown command: {msg}")

    async def stop(self):
        if self._ws is not None:
            await self._ws.close()
            self._ws = None

    async def _handle_event(self, event: dict):
        if "name" not in event:
            return

        if event["name"] == "keepWebserviceAlive":
            self._last_keepalive = time.time() * 1000.0

        # subscribed event
        if event["name"] == self._event_name:
            for callback in self._callbacks:
                await callback(event=event)
