# -*- coding: UTF-8 -*-
import aiounittest
from unittest.mock import Mock, patch

from pydigitalstrom.devices.areablind import DSAreaBlind
from tests.common import get_testclient


class TestAreaBlind(aiounittest.AsyncTestCase):
    async def test_open(self):
        with patch('pydigitalstrom.devices.areablind.DSAreaBlind.request',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_request:
            device = DSAreaBlind(client=get_testclient(), data=dict(
                id=1, zone_id=1, zone_name='Room', area_id=2, area_name='Area'))

            await device.open()
            mock_request.assert_called_with(
                url='/json/zone/callScene?id={zone}&groupID=2&'
                    'sceneNumber={scene}&force=true', zone=1, scene=7,
                check_result=False)
            self.assertFalse(device._is_closed)

    async def test_close(self):
        with patch('pydigitalstrom.devices.areablind.DSAreaBlind.request',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_request:
            device = DSAreaBlind(client=get_testclient(), data=dict(
                id=1, zone_id=1, zone_name='Room', area_id=2, area_name='Area'))

            await device.close()
            mock_request.assert_called_with(
                url='/json/zone/callScene?id={zone}&groupID=2&'
                    'sceneNumber={scene}&force=true', zone=1, scene=2,
                check_result=False)
            self.assertTrue(device._is_closed)
