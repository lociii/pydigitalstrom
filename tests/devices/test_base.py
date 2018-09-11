# -*- coding: UTF-8 -*-
import aiounittest
from unittest.mock import Mock, patch

from pydigitalstrom.devices.base import DSDevice
from tests.common import get_testclient


class TestDevice(aiounittest.AsyncTestCase):
    def test_initialize(self):
        device = DSDevice(client=get_testclient(), data=dict(id=5, var='set'))
        self.assertEqual(device._id, 5)
        self.assertEqual(device._data, dict(id=5, var='set'))

    def test_get_data(self):
        device = DSDevice(client=get_testclient(), data=dict(id=5, var='set'))
        self.assertEqual(device.get_data(), dict(id=5, var='set'))

    def test_name(self):
        device = DSDevice(client=get_testclient(),
                          data=dict(id=5, name='whatever'))
        self.assertEqual(device.name, 'whatever')

    def test_unique_id(self):
        device = DSDevice(client=get_testclient(), data=dict(id=864))
        self.assertEqual(device.unique_id, 864)

    async def test_request_plain_check_result_true(self):
        with patch('pydigitalstrom.client.DSClient.request',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_request:
            device = DSDevice(client=get_testclient(), data=dict(id=1))
            await device.request(url='abc.de', check_result=True)
            mock_request.assert_called_with(url='abc.de', check_result=True)

    async def test_request_plain_check_result_false(self):
        with patch('pydigitalstrom.client.DSClient.request',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_request:
            device = DSDevice(client=get_testclient(), data=dict(id=1))
            await device.request(url='abc.de', check_result=False)
            mock_request.assert_called_with(url='abc.de', check_result=False)

    async def test_request_params_from_data(self):
        with patch('pydigitalstrom.client.DSClient.request',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_request:
            device = DSDevice(client=get_testclient(),
                              data=dict(id=1, foo='bar'))
            await device.request(url='abc{foo}.de', check_result=True)
            mock_request.assert_called_with(url='abcbar.de', check_result=True)

    async def test_request_params_check_result_true(self):
        with patch('pydigitalstrom.client.DSClient.request',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_request:
            device = DSDevice(client=get_testclient(), data=dict(id=287))
            await device.request(url='abc{id}.de', check_result=True)
            mock_request.assert_called_with(url='abc287.de', check_result=True)

    async def test_request_params_check_result_false(self):
        with patch('pydigitalstrom.client.DSClient.request',
                   Mock(return_value=aiounittest.futurized(dict()))) as \
                mock_request:
            device = DSDevice(client=get_testclient(), data=dict(id=287))
            await device.request(url='abc{id}.de', check_result=False)
            mock_request.assert_called_with(url='abc287.de', check_result=False)
