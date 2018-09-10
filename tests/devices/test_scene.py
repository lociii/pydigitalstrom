# -*- coding: UTF-8 -*-
import unittest
from unittest.mock import MagicMock

from pydigitalstrom.devices.scene import DSScene
from tests.common import get_testclient


class TestBlind(unittest.TestCase):
    def test_initial(self):
        device = DSScene(client=get_testclient(), data=dict(zone_id=1, scene_id=2))
        self.assertEqual(device._data, dict(zone_id=1, scene_id=2))

    def test_name(self):
        device = DSScene(client=get_testclient(), data=dict(zone_name='Kitchen', name='Ceiling light'))
        self.assertEqual(device.name, 'Kitchen / Ceiling light')

    def test_unique_id(self):
        device = DSScene(client=get_testclient(), data=dict(zone_id=1, scene_id=2))
        self.assertEqual(device.unique_id, '1.2')

    def test_turn_on(self):
        device = DSScene(client=get_testclient(), data=dict(zone_id=1, scene_id=2))
        device.request = MagicMock()
        device.turn_on()
        device.request.assert_called_with(url='/json/zone/callScene?id=1&sceneNumber=2', check_result=False)

    def test_turn_off(self):
        device = DSScene(client=get_testclient(), data=dict(zone_id=1, scene_id=2))
        device.request = MagicMock()
        device.turn_off()
        device.request.assert_called_with(url='/json/zone/undoScene?id=1&sceneNumber=2', check_result=False)
