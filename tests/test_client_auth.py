# -*- coding: UTF-8 -*-
from tempfile import NamedTemporaryFile

import aiounittest
from unittest.mock import Mock, patch

from pydigitalstrom.exceptions import DSException
from tests.common import get_testclient


class TestClientAuth(aiounittest.AsyncTestCase):
    def test_initialize(self):
        client = get_testclient()
        self.assertEqual(client.host, 'https://dss.local:8080')
        self.assertEqual(client.username, 'dssadmin')
        self.assertEqual(client.password, 'password')
        self.assertEqual(client.config_path, '/tmp')
        self.assertEqual(client._apartment_name, 'Apartment')

        self.assertIsNone(client._apptoken)
        self.assertIsNone(client._last_request)
        self.assertIsNone(client._session_id)
        self.assertIsNone(client._server)
        self.assertIsNone(client._meters)
        self.assertIsNone(client._apartment)
        self.assertIsNone(client._devices)
        self.assertIsNone(client._scenes)

    async def test_get_application_token_from_server(self):
        with patch('pydigitalstrom.client.DSClient.raw_request',
                   Mock(return_value=aiounittest.futurized(
                       dict(result=dict(applicationToken=987))))) as \
                mock_raw_request:
            client = get_testclient()
            apptoken = await client.get_application_token_from_server()
            self.assertEqual(apptoken, 987)
            mock_raw_request.assert_called_with(
                '/json/system/requestApplicationToken?applicationName='
                'homeassistant')

        with patch('pydigitalstrom.client.DSClient.raw_request',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_raw_request:
            with self.assertRaises(DSException):
                client = get_testclient()
                await client.get_application_token_from_server()
            mock_raw_request.assert_called_with(
                '/json/system/requestApplicationToken?applicationName='
                'homeassistant')

    async def test_get_temp_token(self):
        with patch('pydigitalstrom.client.DSClient.raw_request',
                   Mock(return_value=aiounittest.futurized(
                       dict(result=dict(token=725))))) as \
                mock_raw_request:
            client = get_testclient()
            temptoken = await client.get_temp_token()
            self.assertEqual(temptoken, 725)
            mock_raw_request.assert_called_with(
                '/json/system/login?user=dssadmin&password=password')

        with patch('pydigitalstrom.client.DSClient.raw_request',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_raw_request:
            with self.assertRaises(DSException):
                client = get_testclient()
                await client.get_temp_token()
            mock_raw_request.assert_called_with(
                '/json/system/login?user=dssadmin&password=password')

    async def test_activate_application_token(self):
        with patch('pydigitalstrom.client.DSClient.raw_request',
                   Mock(return_value=aiounittest.futurized(
                       dict()))) as mock_raw_request:
            client = get_testclient()
            result = await client.activate_application_token(
                apptoken=342, temptoken=4702)
            self.assertTrue(result)
            mock_raw_request.assert_called_with(
                '/json/system/enableToken?applicationToken=342&token=4702')

    async def test_get_session_token(self):
        with patch('pydigitalstrom.client.DSClient.raw_request',
                   Mock(return_value=aiounittest.futurized(
                       dict(result=dict(token=2736))))) as \
                mock_raw_request:
            client = get_testclient()
            sessiontoken = await client.get_session_token(apptoken=3627)
            self.assertEqual(sessiontoken, 2736)
            mock_raw_request.assert_called_with(
                '/json/system/loginApplication?loginToken=3627')

        with patch('pydigitalstrom.client.DSClient.raw_request',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_raw_request:
            with self.assertRaises(DSException):
                client = get_testclient()
                await client.get_session_token(apptoken=3627)
            mock_raw_request.assert_called_with(
                '/json/system/loginApplication?loginToken=3627')

    async def test_get_application_token_source_property(self):
        client = get_testclient()
        client._apptoken = 193221
        apptoken = await client.get_application_token()
        self.assertEqual(apptoken, 193221)

    async def test_get_application_token_source_file(self):
        with NamedTemporaryFile() as tempfile:
            tempfile.write(b'{"apptoken": 283283}')
            tempfile.flush()

            client = get_testclient(config_path=tempfile.name)
            with patch('pydigitalstrom.client.DSClient.get_session_token',
                       Mock(return_value=aiounittest.futurized(dict()))) as \
                    mock_get_session_token:
                apptoken = await client.get_application_token()
                self.assertEqual(apptoken, 283283)
                mock_get_session_token.assert_called_with(
                    apptoken=283283)

    async def test_get_application_token_source_server(self):
        with NamedTemporaryFile() as tempfile:
            client = get_testclient(config_path=tempfile.name)

            with patch(
                'pydigitalstrom.client.DSClient.'
                'get_application_token_from_server',
                Mock(return_value=aiounittest.futurized(73622))) as \
                    mock_get_application_token_from_server:

                with patch('pydigitalstrom.client.DSClient.get_temp_token',
                           Mock(return_value=aiounittest.futurized(36253))) as \
                        mock_get_temp_token:

                    with patch('pydigitalstrom.client.DSClient.'
                               'activate_application_token',
                               Mock(return_value=aiounittest.futurized(
                                   True))) as mock_activate_application_token:

                        apptoken = await client.get_application_token()
                        self.assertEqual(apptoken, 73622)
                        self.assertEqual(client._apptoken, 73622)
                        self.assertTrue(
                            mock_get_application_token_from_server.called)
                        self.assertTrue(mock_get_temp_token.called)
                        mock_activate_application_token.assert_called_with(
                            apptoken=73622, temptoken=36253)
                        self.assertEqual(
                            tempfile.readline(), b'{"apptoken": 73622}')
