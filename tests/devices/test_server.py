# -*- coding: UTF-8 -*-
import aiounittest
from unittest.mock import Mock, patch

from pydigitalstrom.devices.server import DSServer
from tests.common import get_testclient


class TestServer(aiounittest.AsyncTestCase):
    def test_initial(self):
        device = DSServer(
            client=get_testclient(), data=dict(MachineID=1323, y=232))
        self.assertEqual(device._data, dict(
            MachineID=1323, y=232, id=1323, name='Server'))

    def test_get_data(self):
        device = DSServer(
            client=get_testclient(), data=dict(MachineID=1323, y=232))
        self.assertEqual(device.get_data(), dict(
            MachineID=1323, y=232, id=1323, name='Server'))

    async def test_update(self):
        with patch('pydigitalstrom.devices.server.DSServer.request',
                   Mock(return_value=aiounittest.futurized(
                       dict(MachineID=987)))) as mock_request:
            device = DSServer(
                client=get_testclient(), data=dict(MachineID=123))
            await device.update()
            mock_request.assert_called_with(url='/json/system/version')
            self.assertEqual(device.get_data(),
                             dict(MachineID=987, id=987, name='Server'))
