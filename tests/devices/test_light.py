# -*- coding: UTF-8 -*-
import unittest
from unittest.mock import MagicMock

from pydigitalstrom.devices.light import DSLight
from pydigitalstrom.exceptions import DSUnsupportedException
from tests.common import get_testclient


class TestLight(unittest.TestCase):
    def test_is_on(self):
        device = DSLight(client=get_testclient(), data=dict(on=True, id=1))
        self.assertTrue(device.is_on())

        device = DSLight(client=get_testclient(), data=dict(on=False, id=1))
        self.assertFalse(device.is_on())

    def test_is_dimmable(self):
        # no data provided, default is not dimmable
        device = DSLight(client=get_testclient(), data=dict(on=False, id=1))
        self.assertFalse(device.is_dimmable())

        # large light terminals are not dimmable
        device = DSLight(client=get_testclient(), data=dict(on=False, id=1, hwFunction='KL', outputMode=1))
        self.assertFalse(device.is_dimmable())

        # output mode 16 means switched output
        device = DSLight(client=get_testclient(), data=dict(on=False, id=1, hwFunction='KM', outputMode=16))
        self.assertFalse(device.is_dimmable())

        device = DSLight(client=get_testclient(), data=dict(on=False, id=1, hwFunction='KM', outputMode=1))
        self.assertTrue(device.is_dimmable())

    def test_get_brightness(self):
        # non dimmable lights are None by default
        device = DSLight(client=get_testclient(), data=dict(on=False, id=1))
        self.assertIsNone(device.get_brightness())

        # dimmable light is off
        device = DSLight(client=get_testclient(), data=dict(on=False, id=1, hwFunction='KM', outputMode=1))
        self.assertEqual(device.get_brightness(), 0)

        # dimmable light is on, but brightness is not set by default
        device = DSLight(client=get_testclient(), data=dict(on=True, id=1, hwFunction='KM', outputMode=1))
        self.assertIsNone(device.get_brightness())

        # manually set brightness
        device._brightness = 53
        self.assertEqual(device.get_brightness(), 53)

    def test_identify(self):
        device = DSLight(client=get_testclient(), data=dict(on=False, id=1))
        device.request = MagicMock()
        device.identify()
        device.request.assert_called_with(url='/json/device/blink?dsid={id}')

    def test_turn_on(self):
        device = DSLight(client=get_testclient(), data=dict(on=False, id=1))
        device.request = MagicMock()

        # non dimmable light
        device.turn_on()
        device.request.assert_called_with(url='/json/device/turnOn?dsid={id}')
        self.assertTrue(device._state)
        self.assertIsNone(device._brightness)

        # setting brightness on a non dimmable light raises an error
        with self.assertRaises(DSUnsupportedException):
            device.turn_on(brightness=53)

        # make it dimmable but turn on normally
        device._is_dimmable = True
        device.turn_on()
        device.request.assert_called_with(url='/json/device/turnOn?dsid={id}')
        self.assertTrue(device._state)
        self.assertEqual(device._brightness, 255)

        # set brightness
        device.turn_on(brightness=53)
        device.request.assert_called_with(url='/device/setValue?dsid={id}&value={brightness}', brightness=53)
        self.assertTrue(device._state)
        self.assertEqual(device._brightness, 53)

    def test_turn_off(self):
        device = DSLight(client=get_testclient(), data=dict(on=False, id=1))
        device.request = MagicMock()
        device.turn_off()
        device.request.assert_called_with(url='/json/device/turnOff?dsid={id}')
        self.assertFalse(device._state)
        self.assertIsNone(device._brightness)

        device._is_dimmable = True
        device.turn_off()
        device.request.assert_called_with(url='/json/device/turnOff?dsid={id}')
        self.assertFalse(device._state)
        self.assertEqual(device._brightness, 0)

    def test_toggle_on(self):
        device = DSLight(client=get_testclient(), data=dict(on=False, id=1))
        device.turn_on = MagicMock()
        device.turn_off = MagicMock()

        device.toggle()
        self.assertTrue(device.turn_on.called)
        self.assertFalse(device.turn_off.called)

    def test_toggle_off(self):
        device = DSLight(client=get_testclient(), data=dict(on=True, id=1))
        device.turn_on = MagicMock()
        device.turn_off = MagicMock()

        device.toggle()
        self.assertTrue(device.turn_off.called)
        self.assertFalse(device.turn_on.called)

    def test_update_non_dimmable_off(self):
        device = DSLight(client=get_testclient(), data=dict(on=True, id=1))
        device.request = MagicMock(return_value=dict(value=0))
        device.update()
        device.request.assert_called_with(url='/json/device/getOutputValue?dsid={id}&offset=0')
        self.assertFalse(device._state)
        self.assertIsNone(device._brightness)

    def test_update_non_dimmable_on(self):
        device = DSLight(client=get_testclient(), data=dict(on=False, id=1))
        device.request = MagicMock(return_value=dict(value=255))
        device.update()
        device.request.assert_called_with(url='/json/device/getOutputValue?dsid={id}&offset=0')
        self.assertTrue(device._state)
        self.assertIsNone(device._brightness)

    def test_update_dimmable_off(self):
        device = DSLight(client=get_testclient(), data=dict(on=True, id=1))
        device._is_dimmable = True
        device.request = MagicMock(return_value=dict(value=0))
        device.update()
        device.request.assert_called_with(url='/json/device/getOutputValue?dsid={id}&offset=0')
        self.assertFalse(device._state)
        self.assertEqual(device._brightness, 0)

    def test_update_dimmable_on(self):
        device = DSLight(client=get_testclient(), data=dict(on=False, id=1))
        device._is_dimmable = True
        device.request = MagicMock(return_value=dict(value=53))
        device.update()
        device.request.assert_called_with(url='/json/device/getOutputValue?dsid={id}&offset=0')
        self.assertTrue(device._state)
        self.assertEqual(device._brightness, 53)
