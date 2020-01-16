# -*- coding: UTF-8 -*-
import aiounittest
from unittest.mock import Mock, patch

from pydigitalstrom.devices.scene import DSScene, DSColorScene
from tests.common import get_testclient


class TestScene(aiounittest.AsyncTestCase):
    def test_initial(self):
        device = DSScene(
            client=get_testclient(),
            zone_id=1,
            zone_name="zone",
            scene_id=2,
            scene_name="scene",
        )
        self.assertEqual(device.zone_id, 1)
        self.assertEqual(device.zone_name, "zone")
        self.assertEqual(device.scene_id, 2)
        self.assertEqual(device.scene_name, "scene")
        self.assertEqual(device.unique_id, "1_2")

    async def test_turn_on(self):
        with patch(
            "pydigitalstrom.commandstack.DSCommandStack.append",
            Mock(return_value=aiounittest.futurized(dict())),
        ) as mock_stack_append:
            device = DSScene(
                client=get_testclient(),
                zone_id=1,
                zone_name="zone",
                scene_id=2,
                scene_name="scene",
            )
            await device.turn_on()
            mock_stack_append.assert_called_with(
                url="/json/zone/callScene?id=1&sceneNumber=2&force=true",
            )


class TestColorScene(aiounittest.AsyncTestCase):
    def test_initial(self):
        device = DSColorScene(
            client=get_testclient(),
            zone_id=1,
            zone_name="zone",
            scene_id=2,
            scene_name="scene",
            color=1,
        )
        self.assertEqual(device.zone_id, 1)
        self.assertEqual(device.zone_name, "zone")
        self.assertEqual(device.scene_id, 2)
        self.assertEqual(device.scene_name, "scene")
        self.assertEqual(device.color, 1)
        self.assertEqual(device.unique_id, "1_1_2")

    async def test_turn_on(self):
        with patch(
            "pydigitalstrom.commandstack.DSCommandStack.append",
            Mock(return_value=aiounittest.futurized(dict())),
        ) as mock_stack_append:
            device = DSColorScene(
                client=get_testclient(),
                zone_id=1,
                zone_name="zone",
                scene_id=2,
                scene_name="scene",
                color=1,
            )
            await device.turn_on()
            mock_stack_append.assert_called_with(
                url="/json/zone/callScene?id=1&sceneNumber=2&groupID=1&" "force=true",
            )
