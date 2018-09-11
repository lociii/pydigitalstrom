# -*- coding: UTF-8 -*-
import aiounittest
from unittest.mock import Mock, patch

from pydigitalstrom.devices.blind import DSBlind
from pydigitalstrom.exceptions import DSParameterException
from tests.common import get_testclient


class TestBlind(aiounittest.AsyncTestCase):
    def test_initial_position(self):
        device = DSBlind(client=get_testclient(), data=dict(id=1))
        self.assertEqual(device.get_position(), 0)

    async def test_set_position(self):
        device = DSBlind(client=get_testclient(), data=dict(id=1))

        with self.assertRaises(TypeError):
            await device.set_position('hello')

        with self.assertRaises(DSParameterException):
            await device.set_position(-1)

        with self.assertRaises(DSParameterException):
            await device.set_position(256)

        with patch('pydigitalstrom.devices.blind.DSBlind.request',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_request:
            await device.set_position(53)
            mock_request.assert_called_with(
                url='/json/device/setValue?dsid={id}&value={position}',
                position=53, check_result=False)

    async def test_stop(self):
        with patch('pydigitalstrom.devices.blind.DSBlind.request',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_request:
            device = DSBlind(client=get_testclient(), data=dict(id=1))
            await device.stop()
            mock_request.assert_called_with(
                url='/json/device/callScene?dsid={id}&sceneNumber=15',
                check_result=False)

    async def test_move_up(self):
        with patch('pydigitalstrom.devices.blind.DSBlind.request',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_request:
            device = DSBlind(client=get_testclient(), data=dict(id=1))
            await device.move_up()
            mock_request.assert_called_with(
                url='/json/device/callScene?dsid={id}&sceneNumber=14',
                check_result=False)

    async def test_move_down(self):
        with patch('pydigitalstrom.devices.blind.DSBlind.request',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_request:
            device = DSBlind(client=get_testclient(), data=dict(id=1))
            await device.move_down()
            mock_request.assert_called_with(
                url='/json/device/callScene?dsid={id}&sceneNumber=13',
                check_result=False)

    async def test_update(self):
        with patch('pydigitalstrom.devices.blind.DSBlind.request',
                   Mock(return_value=aiounittest.futurized(
                       dict(value=53)))) as mock_request:
            device = DSBlind(client=get_testclient(), data=dict(id=1))
            await device.update()
            mock_request.assert_called_with(
                url='/json/device/getOutputValue?dsid={id}&offset=0')
            self.assertEqual(device.get_position(), 53)
