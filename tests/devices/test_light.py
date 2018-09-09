# -*- coding: UTF-8 -*-
import unittest
from unittest.mock import MagicMock

from pydigitalstrom.devices.light import DSLight
from pydigitalstrom.exceptions import DSUnsupportedException
from tests.common import get_testclient


class TestLight(unittest.TestCase):
    def test_is_on(self):
        light = DSLight(client=get_testclient(), data=dict(on=True, id=1))
        self.assertTrue(light.is_on())

        light = DSLight(client=get_testclient(), data=dict(on=False, id=1))
        self.assertFalse(light.is_on())

    def test_is_dimmable(self):
        # no data provided, default is not dimmable
        light = DSLight(client=get_testclient(), data=dict(on=False, id=1))
        self.assertFalse(light.is_dimmable())

        # large light terminals are not dimmable
        light = DSLight(client=get_testclient(), data=dict(on=False, id=1, hwFunction='KL', outputMode=1))
        self.assertFalse(light.is_dimmable())

        # output mode 16 means switched output
        light = DSLight(client=get_testclient(), data=dict(on=False, id=1, hwFunction='KM', outputMode=16))
        self.assertFalse(light.is_dimmable())

        light = DSLight(client=get_testclient(), data=dict(on=False, id=1, hwFunction='KM', outputMode=1))
        self.assertTrue(light.is_dimmable())

    def test_get_brightness(self):
        # non dimmable lights are None by default
        light = DSLight(client=get_testclient(), data=dict(on=False, id=1))
        self.assertIsNone(light.get_brightness())

        # dimmable light is off
        light = DSLight(client=get_testclient(), data=dict(on=False, id=1, hwFunction='KM', outputMode=1))
        self.assertEqual(light.get_brightness(), 0)

        # dimmable light is on, but brightness is not set by default
        light = DSLight(client=get_testclient(), data=dict(on=True, id=1, hwFunction='KM', outputMode=1))
        self.assertIsNone(light.get_brightness())

        # manually set brightness
        light._brightness = 53
        self.assertEqual(light.get_brightness(), 53)

    def test_identify(self):
        light = DSLight(client=get_testclient(), data=dict(on=False, id=1))
        light.request = MagicMock()
        light.identify()
        light.request.assert_called_with(url=light.URL_IDENTIFY)

    def test_turn_on(self):
        light = DSLight(client=get_testclient(), data=dict(on=False, id=1))
        light.request = MagicMock()

        # non dimmable light
        light.turn_on()
        light.request.assert_called_with(url=light.URL_TURN_ON)
        self.assertTrue(light._state)
        self.assertIsNone(light._brightness)

        # setting brightness on a non dimmable device raises an error
        with self.assertRaises(DSUnsupportedException):
            light.turn_on(brightness=53)

        # make it dimmable but turn on normally
        light._is_dimmable = True
        light.turn_on()
        light.request.assert_called_with(url=light.URL_TURN_ON)
        self.assertTrue(light._state)
        self.assertEqual(light._brightness, 255)

        # set brightness
        light.turn_on(brightness=53)
        light.request.assert_called_with(url=light.URL_SET_BRIGHTNESS, brightness=53)
        self.assertTrue(light._state)
        self.assertEqual(light._brightness, 53)

    def test_turn_off(self):
        light = DSLight(client=get_testclient(), data=dict(on=False, id=1))
        light.request = MagicMock()
        light.turn_off()
        light.request.assert_called_with(url=light.URL_TURN_OFF)
        self.assertFalse(light._state)
        self.assertIsNone(light._brightness)

        light._is_dimmable = True
        light.turn_off()
        light.request.assert_called_with(url=light.URL_TURN_OFF)
        self.assertFalse(light._state)
        self.assertEqual(light._brightness, 0)

    def test_toggle_on(self):
        light = DSLight(client=get_testclient(), data=dict(on=False, id=1))
        light.turn_on = MagicMock()
        light.turn_off = MagicMock()

        light.toggle()
        self.assertTrue(light.turn_on.called)
        self.assertFalse(light.turn_off.called)

    def test_toggle_off(self):
        light = DSLight(client=get_testclient(), data=dict(on=True, id=1))
        light.turn_on = MagicMock()
        light.turn_off = MagicMock()

        light.toggle()
        self.assertTrue(light.turn_off.called)
        self.assertFalse(light.turn_on.called)

    def test_update_non_dimmable_off(self):
        light = DSLight(client=get_testclient(), data=dict(on=True, id=1))
        light.request = MagicMock(return_value=dict(value=0))
        light.update()
        light.request.assert_called_with(url=light.URL_UPDATE)
        self.assertFalse(light._state)
        self.assertIsNone(light._brightness)

    def test_update_non_dimmable_on(self):
        light = DSLight(client=get_testclient(), data=dict(on=False, id=1))
        light.request = MagicMock(return_value=dict(value=255))
        light.update()
        light.request.assert_called_with(url=light.URL_UPDATE)
        self.assertTrue(light._state)
        self.assertIsNone(light._brightness)

    def test_update_dimmable_off(self):
        light = DSLight(client=get_testclient(), data=dict(on=True, id=1))
        light._is_dimmable = True
        light.request = MagicMock(return_value=dict(value=0))
        light.update()
        light.request.assert_called_with(url=light.URL_UPDATE)
        self.assertFalse(light._state)
        self.assertEqual(light._brightness, 0)

    def test_update_dimmable_on(self):
        light = DSLight(client=get_testclient(), data=dict(on=False, id=1))
        light._is_dimmable = True
        light.request = MagicMock(return_value=dict(value=53))
        light.update()
        light.request.assert_called_with(url=light.URL_UPDATE)
        self.assertTrue(light._state)
        self.assertEqual(light._brightness, 53)
