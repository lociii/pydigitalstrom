import aiounittest
from unittest.mock import Mock, patch

from pydigitalstrom.apptokenhandler import DSAppTokenHandler
from pydigitalstrom.exceptions import DSException
from tests.common import TEST_HOST, TEST_PORT, TEST_USERNAME, TEST_PASSWORD


class TestAppTokenHandler(aiounittest.AsyncTestCase):
    def get_test_handler(
        self,
        host=TEST_HOST,
        port=TEST_PORT,
        username=TEST_USERNAME,
        password=TEST_PASSWORD,
    ):
        return DSAppTokenHandler(
            host=host, port=port, username=username, password=password
        )

    def test_initialize(self):
        handler = self.get_test_handler()
        self.assertEqual(handler.host, TEST_HOST)
        self.assertEqual(handler.port, TEST_PORT)
        self.assertEqual(handler.username, TEST_USERNAME)
        self.assertEqual(handler.password, TEST_PASSWORD)

    async def test_get_application_token_from_server(self):
        with patch(
            "pydigitalstrom.requesthandler.DSRequestHandler.raw_request",
            Mock(
                return_value=aiounittest.futurized(
                    dict(result=dict(applicationToken=987))
                )
            ),
        ) as mock_raw_request:
            handler = self.get_test_handler()
            apptoken = await handler.get_application_token_from_server()
            self.assertEqual(apptoken, 987)
            mock_raw_request.assert_called_with(
                "/json/system/requestApplicationToken?applicationName=" "homeassistant"
            )

        with patch(
            "pydigitalstrom.requesthandler.DSRequestHandler.raw_request",
            Mock(return_value=aiounittest.futurized(dict())),
        ) as mock_raw_request:
            with self.assertRaises(DSException):
                handler = self.get_test_handler()
                await handler.get_application_token_from_server()
            mock_raw_request.assert_called_with(
                "/json/system/requestApplicationToken?applicationName=" "homeassistant"
            )

    async def test_get_temp_token(self):
        with patch(
            "pydigitalstrom.requesthandler.DSRequestHandler.raw_request",
            Mock(return_value=aiounittest.futurized(dict(result=dict(token=725)))),
        ) as mock_raw_request:
            handler = self.get_test_handler()
            temptoken = await handler.get_temp_token()
            self.assertEqual(temptoken, 725)
            mock_raw_request.assert_called_with(
                "/json/system/login?user=dssadmin&password=password"
            )

        with patch(
            "pydigitalstrom.requesthandler.DSRequestHandler.raw_request",
            Mock(return_value=aiounittest.futurized(dict())),
        ) as mock_raw_request:
            with self.assertRaises(DSException):
                handler = self.get_test_handler()
                await handler.get_temp_token()
            mock_raw_request.assert_called_with(
                "/json/system/login?user=dssadmin&password=password"
            )

    async def test_activate_application_token(self):
        with patch(
            "pydigitalstrom.requesthandler.DSRequestHandler.raw_request",
            Mock(return_value=aiounittest.futurized(dict())),
        ) as mock_raw_request:
            handler = self.get_test_handler()
            result = await handler.activate_application_token(
                apptoken=342, temptoken=4702
            )
            self.assertTrue(result)
            mock_raw_request.assert_called_with(
                "/json/system/enableToken?applicationToken=342&token=4702"
            )
