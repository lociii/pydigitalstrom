# -*- coding: UTF-8 -*-
import aiounittest
from unittest.mock import Mock, patch

from pydigitalstrom.devices.arealight import DSAreaLight
from tests.common import get_testclient


class TestAreaLight(aiounittest.AsyncTestCase):
    async def test_turn_on(self):
        with patch('pydigitalstrom.devices.arealight.DSAreaLight.request',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_request:
            device = DSAreaLight(client=get_testclient(), data=dict(
                id=1, zone_id=1, zone_name='Room', area_id=2, area_name='Area'))

            await device.turn_on()
            mock_request.assert_called_with(
                url='/json/zone/callScene?id={zone}&groupID=1&'
                    'sceneNumber={scene}&force=true', zone=1, scene=7,
                check_result=False)
            self.assertTrue(device._state)

    async def test_turn_off(self):
        with patch('pydigitalstrom.devices.arealight.DSAreaLight.request',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_request:
            device = DSAreaLight(client=get_testclient(), data=dict(
                id=1, zone_id=1, zone_name='Room', area_id=2, area_name='Area'))

            await device.turn_off()
            mock_request.assert_called_with(
                url='/json/zone/callScene?id={zone}&groupID=1&'
                    'sceneNumber={scene}&force=true', zone=1, scene=2,
                check_result=False)
            self.assertFalse(device._state)

    async def test_toggle_none(self):
        with patch('pydigitalstrom.devices.arealight.DSAreaLight.turn_on',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_turn_on:
            with patch('pydigitalstrom.devices.arealight.DSAreaLight.turn_off',
                       Mock(return_value=aiounittest.futurized(dict()))) as \
                    mock_turn_off:
                device = DSAreaLight(client=get_testclient(), data=dict(
                    id=1, zone_id=1, zone_name='Room', area_id=2,
                    area_name='Area'))

                await device.toggle()
                self.assertFalse(mock_turn_on.called)
                self.assertFalse(mock_turn_off.called)

    async def test_toggle_on(self):
        with patch('pydigitalstrom.devices.arealight.DSAreaLight.turn_on',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_turn_on:
            with patch('pydigitalstrom.devices.arealight.DSAreaLight.turn_off',
                       Mock(return_value=aiounittest.futurized(dict()))) as \
                    mock_turn_off:
                device = DSAreaLight(client=get_testclient(), data=dict(
                    id=1, zone_id=1, zone_name='Room', area_id=2,
                    area_name='Area'))
                device._state = False

                await device.toggle()
                self.assertTrue(mock_turn_on.called)
                self.assertFalse(mock_turn_off.called)

    async def test_toggle_off(self):
        with patch('pydigitalstrom.devices.arealight.DSAreaLight.turn_on',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_turn_on:
            with patch('pydigitalstrom.devices.arealight.DSAreaLight.turn_off',
                       Mock(return_value=aiounittest.futurized(dict()))) as \
                    mock_turn_off:
                device = DSAreaLight(client=get_testclient(), data=dict(
                    id=1, zone_id=1, zone_name='Room', area_id=2,
                    area_name='Area'))
                device._state = True

                await device.toggle()
                self.assertFalse(mock_turn_on.called)
                self.assertTrue(mock_turn_off.called)
