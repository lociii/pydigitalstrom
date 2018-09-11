# -*- coding: UTF-8 -*-
import aiounittest
from unittest.mock import Mock, patch

from pydigitalstrom.devices.switch import DSSwitchSensor, DSSwitch
from tests.common import get_testclient


class TestSwitchSensor(aiounittest.AsyncTestCase):
    def test_initial_on(self):
        device = DSSwitchSensor(
            client=get_testclient(), data=dict(id=1, on=True))
        self.assertTrue(device.is_on())

    def test_initial_off(self):
        device = DSSwitchSensor(
            client=get_testclient(), data=dict(id=1, on=False))
        self.assertFalse(device.is_on())

    async def test_update_off_to_off(self):
        with patch('pydigitalstrom.devices.switch.DSSwitchSensor.request',
                   Mock(return_value=aiounittest.futurized(
                       dict(value=0)))) as mock_request:
            device = DSSwitchSensor(
                client=get_testclient(), data=dict(id=1, on=False))
            await device.update()
            mock_request.assert_called_with(
                url='/json/device/getOutputValue?dsid={id}&offset=0')
            self.assertFalse(device.is_on())

    async def test_update_off_to_on(self):
        with patch('pydigitalstrom.devices.switch.DSSwitchSensor.request',
                   Mock(return_value=aiounittest.futurized(
                       dict(value=100)))) as mock_request:
            device = DSSwitchSensor(
                client=get_testclient(), data=dict(id=1, on=False))
            await device.update()
            mock_request.assert_called_with(
                url='/json/device/getOutputValue?dsid={id}&offset=0')
            self.assertTrue(device.is_on())

    async def test_update_on_to_on(self):
        with patch('pydigitalstrom.devices.switch.DSSwitchSensor.request',
                   Mock(return_value=aiounittest.futurized(
                       dict(value=100)))) as mock_request:
            device = DSSwitchSensor(
                client=get_testclient(), data=dict(id=1, on=True))
            await device.update()
            mock_request.assert_called_with(
                url='/json/device/getOutputValue?dsid={id}&offset=0')
            self.assertTrue(device.is_on())

    async def test_update_on_to_off(self):
        with patch('pydigitalstrom.devices.switch.DSSwitchSensor.request',
                   Mock(return_value=aiounittest.futurized(
                       dict(value=0)))) as mock_request:
            device = DSSwitchSensor(
                client=get_testclient(), data=dict(id=1, on=True))
            await device.update()
            mock_request.assert_called_with(
                url='/json/device/getOutputValue?dsid={id}&offset=0')
            self.assertFalse(device.is_on())


class TestSwitch(aiounittest.AsyncTestCase):
    async def test_turn_on(self):
        with patch('pydigitalstrom.devices.switch.DSSwitch.request',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_request:
            device = DSSwitch(client=get_testclient(),
                              data=dict(id=1, on=False))

            await device.turn_on()
            mock_request.assert_called_with(
                url='/json/device/turnOn?dsid={id}', check_result=False)
            self.assertTrue(device._state)

    async def test_turn_off(self):
        with patch('pydigitalstrom.devices.switch.DSSwitch.request',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_request:
            device = DSSwitch(client=get_testclient(),
                              data=dict(id=1, on=True))

            await device.turn_off()
            mock_request.assert_called_with(
                url='/json/device/turnOff?dsid={id}', check_result=False)
            self.assertFalse(device._state)

    async def test_toggle_on(self):
        with patch('pydigitalstrom.devices.switch.DSSwitch.turn_on',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_turn_on:
            with patch('pydigitalstrom.devices.switch.DSSwitch.turn_off',
                       Mock(return_value=aiounittest.futurized(dict()))) as \
                    mock_turn_off:
                device = DSSwitch(
                    client=get_testclient(), data=dict(on=False, id=1))

                await device.toggle()
                self.assertTrue(mock_turn_on.called)
                self.assertFalse(mock_turn_off.called)

    async def test_toggle_off(self):
        with patch('pydigitalstrom.devices.switch.DSSwitch.turn_on',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_turn_on:
            with patch('pydigitalstrom.devices.switch.DSSwitch.turn_off',
                       Mock(return_value=aiounittest.futurized(dict()))) as \
                    mock_turn_off:
                device = DSSwitch(
                    client=get_testclient(), data=dict(on=True, id=1))

                await device.toggle()
                self.assertTrue(mock_turn_off.called)
                self.assertFalse(mock_turn_on.called)
