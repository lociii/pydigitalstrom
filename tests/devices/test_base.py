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

    async def test_request_enqueued(self):
        with patch(
            "pydigitalstrom.commandstack.DSCommandStack.append",
            Mock(return_value=aiounittest.futurized(dict())),
        ) as mock_stack_append:
            device = DSDevice(client=get_testclient(), device_id=5, device_name="test")
            await device.request(url="abc.de")
            mock_stack_append.assert_called_with(url="abc.de")

    async def test_request_plain(self):
        with patch(
            "pydigitalstrom.commandstack.DSCommandStack.append",
            Mock(return_value=aiounittest.futurized(dict())),
        ) as mock_stack_append:
            device = DSDevice(client=get_testclient(), device_id=5, device_name="test")
            await device.request(url="abc.de")
            mock_stack_append.assert_called_with(url="abc.de")

    async def test_request_with_data(self):
        with patch(
            "pydigitalstrom.commandstack.DSCommandStack.append",
            Mock(return_value=aiounittest.futurized(dict())),
        ) as mock_stack_append:
            device = DSDevice(client=get_testclient(), device_id=5, device_name="test")
            await device.request(url="abc.de?{x}", x="hello")
            mock_stack_append.assert_called_with(url="abc.de?hello")
