# -*- coding: UTF-8 -*-
import asyncio
from contextlib import suppress


class DSEventListener(object):
    def __init__(self, client, event_id, event_name, timeout, loop=None):
        self.client = client
        self.event_id = event_id
        self.event_name = event_name
        self.timeout = timeout
        self.loop = loop
        self.is_started = False
        self._task = None
        self._callbacks = []

    async def start(self):
        if not self.is_started:
            await self.client.event_subscribe(
                event_id=self.event_id, event_name=self.event_name)
            self.is_started = True
            # Start task to call func periodically:
            self._task = asyncio.ensure_future(self._run(), loop=self.loop)

    async def stop(self):
        if self.is_started:
            await self.client.event_unsubscribe(
                event_id=self.event_id, event_name=self.event_name)
            self.is_started = False
            # Stop task and await it stopped:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    async def _run(self):
        while True:
            data = await self.client.event_poll(
                event_id=self.event_id, timeout=self.timeout)
            await self._handle_events(data=data)
            await asyncio.sleep(self.timeout, loop=self.loop)

    async def register(self, callback):
        self._callbacks.append(callback)

    async def _handle_events(self, data):
        if 'events' not in data or not data['events']:
            return

        for event in data['events']:
            if 'name' not in event:
                continue
            for callback in self._callbacks:
                await callback(event=event)
