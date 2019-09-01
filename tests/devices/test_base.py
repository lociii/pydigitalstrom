# -*- coding: UTF-8 -*-
import aiounittest
from unittest.mock import Mock, patch

from pydigitalstrom.devices.base import DSDevice
from tests.common import get_testclient


class TestDevice(aiounittest.AsyncTestCase):
    def test_attributes(self):
        device = DSDevice(client=get_testclient(), device_id=5, device_name="test")
        self.assertEqual(device._id, 5)
        self.assertEqual(device._name, "test")

    def test_name(self):
        device = DSDevice(client=get_testclient(), device_id=5, device_name="test")
        self.assertEqual(device.name, "test")

    def test_unique_id(self):
        device = DSDevice(client=get_testclient(), device_id=5, device_name="test")
        self.assertEqual(device.unique_id, 5)

    async def test_request_plain_check_result_true(self):
        with patch(
            "pydigitalstrom.client.DSClient.request",
            Mock(return_value=aiounittest.futurized(dict())),
        ) as mock_request:
            device = DSDevice(client=get_testclient(), device_id=5, device_name="test")
            await device.request(url="abc.de", check_result=True)
            mock_request.assert_called_with(url="abc.de", check_result=True)

    async def test_request_plain_check_result_false(self):
        with patch(
            "pydigitalstrom.client.DSClient.request",
            Mock(return_value=aiounittest.futurized(dict())),
        ) as mock_request:
            device = DSDevice(client=get_testclient(), device_id=5, device_name="test")
            await device.request(url="abc.de", check_result=False)
            mock_request.assert_called_with(url="abc.de", check_result=False)

    async def test_request_with_data_check_result_true(self):
        with patch(
            "pydigitalstrom.client.DSClient.request",
            Mock(return_value=aiounittest.futurized(dict())),
        ) as mock_request:
            device = DSDevice(client=get_testclient(), device_id=5, device_name="test")
            await device.request(url="abc.de?{x}", x="hello", check_result=True)
            mock_request.assert_called_with(url="abc.de?hello", check_result=True)

    async def test_request_with_data_check_result_false(self):
        with patch(
            "pydigitalstrom.client.DSClient.request",
            Mock(return_value=aiounittest.futurized(dict())),
        ) as mock_request:
            device = DSDevice(client=get_testclient(), device_id=5, device_name="test")
            await device.request(url="abc.de?{x}", x="hello", check_result=False)
            mock_request.assert_called_with(url="abc.de?hello", check_result=False)
