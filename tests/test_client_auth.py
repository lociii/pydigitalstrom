# -*- coding: UTF-8 -*-
import aiounittest
from unittest.mock import Mock, patch

from pydigitalstrom.exceptions import DSException
from tests.common import get_testclient, TEST_HOST, TEST_TOKEN, TEST_APARTMENT


class TestClientAuth(aiounittest.AsyncTestCase):
    def test_initialize(self):
        client = get_testclient()
        self.assertEqual(client.host, TEST_HOST)
        self.assertEqual(client._apptoken, TEST_TOKEN)
        self.assertEqual(client._apartment_name, TEST_APARTMENT)

        self.assertIsNone(client._last_request)
        self.assertIsNone(client._session_token)
        self.assertEqual(client._scenes, dict())

    async def test_get_session_token(self):
        with patch(
            "pydigitalstrom.client.DSClient.raw_request",
            Mock(return_value=aiounittest.futurized(dict(result=dict(token=2736)))),
        ) as mock_raw_request:
            client = get_testclient()
            sessiontoken = await client.get_session_token()
            self.assertEqual(sessiontoken, 2736)
            mock_raw_request.assert_called_with(
                f"/json/system/loginApplication?loginToken={TEST_TOKEN}"
            )

        with patch(
            "pydigitalstrom.client.DSClient.raw_request",
            Mock(return_value=aiounittest.futurized(dict())),
        ) as mock_raw_request:
            with self.assertRaises(DSException):
                client = get_testclient()
                await client.get_session_token()
            mock_raw_request.assert_called_with(
                f"/json/system/loginApplication?loginToken={TEST_TOKEN}"
            )
