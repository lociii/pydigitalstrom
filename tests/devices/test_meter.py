# -*- coding: UTF-8 -*-
import unittest

import aiounittest
from unittest.mock import Mock, patch

from pydigitalstrom.devices.meter import DSMeter
from tests.common import get_testclient


class TestMeter(aiounittest.AsyncTestCase):
    def test_initial(self):
        device = DSMeter(client=get_testclient(), data=dict(dsid=1))
        self.assertEqual(device.get_current_consumption(), None)
        self.assertEqual(device.get_overall_consumption(), None)
        self.assertEqual(device._id, 1)
        self.assertEqual(device._data, dict(dsid=1))

    def test_get_data(self):
        device = DSMeter(client=get_testclient(), data=dict(dsid=5, var='set'))
        self.assertEqual(device.get_data(), dict(dsid=5, var='set'))

    async def test_update(self):
        with patch('pydigitalstrom.devices.meter.DSMeter.request', Mock()) as \
                mock_request:
            mock_request.side_effect = [
                aiounittest.futurized(
                    dict(circuits=[dict(dsid=1, new_value=53)])),
                aiounittest.futurized(dict(consumption=63)),
                aiounittest.futurized(dict(meterValue=73))]
            device = DSMeter(client=get_testclient(), data=dict(dsid=1))
            await device.update()

            assert mock_request.mock_calls == [
                unittest.mock.call(url='/json/apartment/getCircuits'),
                unittest.mock.call(
                    url='/json/circuit/getConsumption?id={id}', id=1),
                unittest.mock.call(
                    url='/json/circuit/getEnergyMeterValue?id={id}', id=1)]

            self.assertEqual(device.get_data(), dict(dsid=1, new_value=53))
            self.assertEqual(device.get_current_consumption(), 63)
            self.assertEqual(device.get_overall_consumption(), 73)
