# -*- coding: UTF-8 -*-
import unittest
from unittest.mock import MagicMock

from pydigitalstrom.devices.meter import DSMeter
from tests.common import get_testclient


class TestMeter(unittest.TestCase):
    def test_initial(self):
        device = DSMeter(client=get_testclient(), data=dict(dsid=1))
        self.assertEqual(device.get_current_consumption(), None)
        self.assertEqual(device.get_overall_consumption(), None)
        self.assertEqual(device._id, 1)
        self.assertEqual(device.get_data(), dict(dsid=1))

    def test_update(self):
        device = DSMeter(client=get_testclient(), data=dict(dsid=1))
        device.request = MagicMock()
        device.request.side_effect = [
            dict(circuits=[dict(dsid=1, new_value=53)]),
            dict(consumption=63),
            dict(meterValue=73)]
        device.update()

        assert device.request.mock_calls == [
            unittest.mock.call(url='/json/apartment/getCircuits'),
            unittest.mock.call(url='/json/circuit/getConsumption?id={id}', id=1),
            unittest.mock.call(url='/json/circuit/getEnergyMeterValue?id={id}', id=1)]

        self.assertEqual(device.get_data(), dict(dsid=1, new_value=53))
        self.assertEqual(device.get_current_consumption(), 63)
        self.assertEqual(device.get_overall_consumption(), 73)
