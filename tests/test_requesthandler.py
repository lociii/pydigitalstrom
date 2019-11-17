# -*- coding: UTF-8 -*-
import aiounittest
from aioresponses import aioresponses

from pydigitalstrom.exceptions import DSCommandFailedException, DSRequestException
from tests.common import get_testclient, TEST_HOST, TEST_PORT


class TestRequestHandler(aiounittest.AsyncTestCase):
    async def test_get_aiohttp_session_disable_ssl(self):
        client = get_testclient()
        session = await client.get_aiohttp_session()
        self.assertFalse(session._connector._ssl)

    async def test_raw_request(self):
        client = get_testclient()
        with aioresponses() as mock_get:
            mock_get.get(
                url=f"https://{TEST_HOST}:{TEST_PORT}/json/hello",
                payload=dict(ok=True, ping="pong"),
            )
            response = await client.raw_request(url="/json/hello")
            self.assertEqual(response, dict(ok=True, ping="pong"))

    async def test_raw_request_not_200(self):
        client = get_testclient()
        with aioresponses() as mock_get:
            mock_get.get(url=f"https://{TEST_HOST}:{TEST_PORT}/json/hello", status=400)
            with self.assertRaises(DSRequestException):
                await client.raw_request(url="/json/hello")

    async def test_raw_request_ok_missing(self):
        client = get_testclient()
        with aioresponses() as mock_get:
            mock_get.get(
                url=f"https://{TEST_HOST}:{TEST_PORT}/json/hello",
                payload=dict(ping="pong"),
            )
            with self.assertRaises(DSCommandFailedException):
                await client.raw_request(url="/json/hello")

    async def test_raw_request_ok_false(self):
        client = get_testclient()
        with aioresponses() as mock_get:
            mock_get.get(
                url=f"https://{TEST_HOST}:{TEST_PORT}/json/hello",
                payload=dict(ok=False, ping="pong"),
            )
            with self.assertRaises(DSCommandFailedException):
                await client.raw_request(url="/json/hello")

    async def test_raw_request_invalid_json(self):
        client = get_testclient()
        with aioresponses() as mock_get:
            mock_get.get(
                url=f"https://{TEST_HOST}:{TEST_PORT}/json/hello",
                body=b"{whatever is not json",
            )
            with self.assertRaises(DSRequestException):
                await client.raw_request(url="/json/hello")
