import asyncio

from pydigitalstrom.client import DSClient


class DSCommandStack:
    def __init__(self, client: DSClient):
        self._client = client
        self._stack = list()
        self._task = None

    async def append(self, url: str):
        self._stack.append(url)

    async def execute(self):
        while True:
            # check for command to execute
            if len(self._stack) > 0:
                await self._client.request(url=self._stack.pop(0))

            # sleep for 200ms before next execution to not overload the DS server
            await asyncio.sleep(0.2)

    async def start(self):
        self.task = asyncio.Task(self.execute())

    async def stop(self):
        if self.task:
            self.task.cancel()
