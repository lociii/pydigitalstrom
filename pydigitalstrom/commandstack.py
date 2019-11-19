import asyncio

from pydigitalstrom.client import DSClient


class DSCommandStack:
    def __init__(self, client: DSClient, delay: int = 500):
        self._client = client
        self._stack = list()
        self._task = None
        self._delay = delay

    async def append(self, url: str):
        self._stack.append(url)

    async def execute(self):
        while True:
            # check for command to execute
            if len(self._stack) > 0:
                await self._client.request(url=self._stack.pop(0))

            # sleep for x ms before next execution to not overload the DS server
            await asyncio.sleep(self._delay / 1000)

    async def start(self):
        self.task = asyncio.Task(self.execute())

    async def stop(self):
        if self.task:
            self.task.cancel()
