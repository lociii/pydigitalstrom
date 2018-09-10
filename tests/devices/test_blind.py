# -*- coding: UTF-8 -*-
import unittest
from unittest.mock import MagicMock

from pydigitalstrom.devices.blind import DSBlind
from pydigitalstrom.exceptions import DSParameterException
from tests.common import get_testclient


class TestBlind(unittest.TestCase):
    def test_initial_position(self):
        device = DSBlind(client=get_testclient(), data=dict(id=1))
        self.assertEqual(device.get_position(), 0)

    def test_set_position(self):
        device = DSBlind(client=get_testclient(), data=dict(id=1))
        with self.assertRaises(TypeError):
            device.set_position('hello')

        with self.assertRaises(DSParameterException):
            device.set_position(-1)

        with self.assertRaises(DSParameterException):
            device.set_position(256)

        device.request = MagicMock()
        device.set_position(53)
        device.request.assert_called_with(url='/json/device/setValue?dsid={id}&value={position}', position=53)

    def test_stop(self):
        device = DSBlind(client=get_testclient(), data=dict(id=1))
        device.request = MagicMock()
        device.stop()
        device.request.assert_called_with(url='/json/device/callScene?dsid={id}&sceneNumber=15', check_result=False)

    def test_move_up(self):
        device = DSBlind(client=get_testclient(), data=dict(id=1))
        device.request = MagicMock()
        device.move_up()
        device.request.assert_called_with(url='/json/device/callScene?dsid={id}&sceneNumber=14', check_result=False)

    def test_move_down(self):
        device = DSBlind(client=get_testclient(), data=dict(id=1))
        device.request = MagicMock()
        device.move_down()
        device.request.assert_called_with(url='/json/device/callScene?dsid={id}&sceneNumber=13', check_result=False)

    def test_update(self):
        device = DSBlind(client=get_testclient(), data=dict(id=1))
        device.request = MagicMock(return_value=dict(value=53))
        device.update()
        device.request.assert_called_with(url='/json/device/getOutputValue?dsid={id}&offset=0')
        self.assertEqual(device.get_position(), 53)
