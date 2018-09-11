# -*- coding: UTF-8 -*-
import aiounittest
from unittest.mock import Mock, patch

from pydigitalstrom.devices.scene import DSScene
from tests.common import get_testclient


class TestScene(aiounittest.AsyncTestCase):
    def test_initial(self):
        device = DSScene(
            client=get_testclient(), data=dict(zone_id=1, zone_name='zone',
                                               scene_id=2, scene_name='scene'))
        self.assertEqual(device._data, dict(zone_id=1, zone_name='zone',
                                            scene_id=2, scene_name='scene',
                                            id='1.2', name='zone / scene'))

    async def test_turn_on(self):
        with patch('pydigitalstrom.devices.scene.DSScene.request',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_request:
            device = DSScene(
                client=get_testclient(), data=dict(
                    zone_id=1, zone_name='zone',
                    scene_id=2, scene_name='scene'))
            await device.turn_on()
            mock_request.assert_called_with(
                url='/json/zone/callScene?id=1&sceneNumber=2',
                check_result=False)

    async def test_turn_off(self):
        with patch('pydigitalstrom.devices.scene.DSScene.request',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_request:
            device = DSScene(
                client=get_testclient(), data=dict(
                    zone_id=1, zone_name='zone',
                    scene_id=2, scene_name='scene'))
            await device.turn_off()
            mock_request.assert_called_with(
                url='/json/zone/undoScene?id=1&sceneNumber=2',
                check_result=False)
