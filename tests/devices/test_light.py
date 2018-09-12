# -*- coding: UTF-8 -*-
import aiounittest
from unittest.mock import Mock, patch

from pydigitalstrom.devices.light import DSLight
from pydigitalstrom.exceptions import DSUnsupportedException
from tests.common import get_testclient


class TestLight(aiounittest.AsyncTestCase):
    def test_is_on(self):
        device = DSLight(client=get_testclient(), data=dict(
            on=True, id=1, outputMode=16))
        self.assertTrue(device.is_on())

        device = DSLight(client=get_testclient(), data=dict(
            on=False, id=1, outputMode=16))
        self.assertFalse(device.is_on())

    def test_is_dimmable(self):
        # no data provided, default is not dimmable
        with self.assertRaises(DSUnsupportedException):
            DSLight(client=get_testclient(), data=dict(
                on=False, id=1, outputMode=1))

        # large light terminals are not dimmable
        device = DSLight(client=get_testclient(), data=dict(
            on=False, id=1, outputMode=16))
        self.assertFalse(device.is_dimmable())

        # output mode 16 means switched output
        device = DSLight(client=get_testclient(), data=dict(
            on=False, id=1, outputMode=16))
        self.assertFalse(device.is_dimmable())

        device = DSLight(client=get_testclient(), data=dict(
            on=False, id=1, outputMode=22))
        self.assertTrue(device.is_dimmable())

    def test_get_brightness(self):
        # non dimmable lights throw an exception
        device = DSLight(client=get_testclient(), data=dict(
            on=False, id=1, outputMode=16))
        with self.assertRaises(DSUnsupportedException):
            self.assertIsNone(device.get_brightness())

        # dimmable light is off
        device = DSLight(client=get_testclient(), data=dict(
            on=False, id=1, outputMode=22))
        self.assertEqual(device.get_brightness(), 0)

        # dimmable light is on, but brightness is not set by default
        device = DSLight(client=get_testclient(), data=dict(
            on=True, id=1, outputMode=22))
        self.assertIsNone(device.get_brightness())

        # manually set brightness
        device._brightness = 53
        self.assertEqual(device.get_brightness(), 53)

    async def test_identify(self):
        with patch('pydigitalstrom.devices.light.DSLight.request',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_request:
            device = DSLight(client=get_testclient(), data=dict(
                on=False, id=1, outputMode=16))
            await device.identify()
            mock_request.assert_called_with(
                url='/json/device/blink?dsid={id}', check_result=False)

    async def test_turn_on(self):
        with patch('pydigitalstrom.devices.light.DSLight.request',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_request:
            device = DSLight(client=get_testclient(), data=dict(
                on=False, id=1, outputMode=16))

            # non dimmable light
            await device.turn_on()
            mock_request.assert_called_with(
                url='/json/device/turnOn?dsid={id}', check_result=False)
            self.assertTrue(device._state)
            self.assertIsNone(device._brightness)

            # setting brightness on a non dimmable light raises an error
            with self.assertRaises(DSUnsupportedException):
                await device.turn_on(brightness=53)

            # make it dimmable but turn on normally
            device._is_dimmable = True
            await device.turn_on()
            mock_request.assert_called_with(
                url='/json/device/turnOn?dsid={id}', check_result=False)
            self.assertTrue(device._state)
            self.assertEqual(device._brightness, 255)

            # set brightness
            await device.turn_on(brightness=53)
            mock_request.assert_called_with(
                url='/device/setValue?dsid={id}&value={brightness}',
                brightness=53, check_result=False)
            self.assertTrue(device._state)
            self.assertEqual(device._brightness, 53)

    async def test_turn_off(self):
        with patch('pydigitalstrom.devices.light.DSLight.request',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_request:
            device = DSLight(client=get_testclient(), data=dict(
                on=False, id=1, outputMode=16))
            await device.turn_off()
            mock_request.assert_called_with(
                url='/json/device/turnOff?dsid={id}', check_result=False)
            self.assertFalse(device._state)
            self.assertIsNone(device._brightness)

            device._is_dimmable = True
            await device.turn_off()
            mock_request.assert_called_with(
                url='/json/device/turnOff?dsid={id}', check_result=False)
            self.assertFalse(device._state)
            self.assertEqual(device._brightness, 0)

    async def test_toggle_on(self):
        with patch('pydigitalstrom.devices.light.DSLight.turn_on',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_turn_on:
            with patch('pydigitalstrom.devices.light.DSLight.turn_off',
                       Mock(return_value=aiounittest.futurized(dict()))) as \
                    mock_turn_off:
                device = DSLight(
                    client=get_testclient(), data=dict(
                        on=False, id=1, outputMode=16))

                await device.toggle()
                self.assertTrue(mock_turn_on.called)
                self.assertFalse(mock_turn_off.called)

    async def test_toggle_off(self):
        with patch('pydigitalstrom.devices.light.DSLight.turn_on',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_turn_on:
            with patch('pydigitalstrom.devices.light.DSLight.turn_off',
                       Mock(return_value=aiounittest.futurized(dict()))) as \
                    mock_turn_off:
                device = DSLight(
                    client=get_testclient(), data=dict(
                        on=True, id=1, outputMode=16))

                await device.toggle()
                self.assertTrue(mock_turn_off.called)
                self.assertFalse(mock_turn_on.called)

    async def test_update_non_dimmable_off(self):
        with patch('pydigitalstrom.devices.light.DSLight.request',
                   Mock(return_value=aiounittest.futurized(dict(value=0)))) as \
                mock_request:
            device = DSLight(client=get_testclient(), data=dict(
                on=True, id=1, outputMode=16))
            await device.update()
            mock_request.assert_called_with(
                url='/json/device/getOutputValue?dsid={id}&offset=0')
            self.assertFalse(device._state)
            self.assertIsNone(device._brightness)

    async def test_update_non_dimmable_on(self):
        with patch('pydigitalstrom.devices.light.DSLight.request',
                   Mock(return_value=aiounittest.futurized(
                       dict(value=255)))) as mock_request:
            device = DSLight(client=get_testclient(), data=dict(
                on=False, id=1, outputMode=16))
            await device.update()
            mock_request.assert_called_with(
                url='/json/device/getOutputValue?dsid={id}&offset=0')
            self.assertTrue(device._state)
            self.assertIsNone(device._brightness)

    async def test_update_dimmable_off(self):
        with patch('pydigitalstrom.devices.light.DSLight.request',
                   Mock(return_value=aiounittest.futurized(
                       dict(value=0)))) as mock_request:
            device = DSLight(client=get_testclient(), data=dict(
                on=True, id=1, outputMode=16))
            device._is_dimmable = True
            await device.update()
            mock_request.assert_called_with(
                url='/json/device/getOutputValue?dsid={id}&offset=0')
            self.assertFalse(device._state)
            self.assertEqual(device._brightness, 0)

    async def test_update_dimmable_on(self):
        with patch('pydigitalstrom.devices.light.DSLight.request',
                   Mock(return_value=aiounittest.futurized(
                       dict(value=53)))) as mock_request:
            device = DSLight(client=get_testclient(), data=dict(
                on=False, id=1, outputMode=16))
            device._is_dimmable = True
            await device.update()
            mock_request.assert_called_with(
                url='/json/device/getOutputValue?dsid={id}&offset=0')
            self.assertTrue(device._state)
            self.assertEqual(device._brightness, 53)
