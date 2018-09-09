# -*- coding: UTF-8 -*-
from pydigitalstrom.client import DSClient
from pydigitalstrom.devices.base import DSDevice


class DSMeter(DSDevice):
    URL_POWER_CONSUMPTION = '/json/circuit/getConsumption?id={id}'
    URL_POWER_METER = '/json/circuit/getEnergyMeterValue?id={id}'

    def __init__(self, client: DSClient, data: dict, *args, **kwargs):
        super().__init__(client=client, *args, **kwargs)
        self._id = data['dsid']
        self._data = data
        self._current_consumption = None
        self._overall_consumption = None

    def get_data(self):
        """
        get meter meta data

        :return: meter meta data
        :rtype: dict
        """
        return self._data

    def update(self):
        """
        update meter meta data and power consumption info
        """
        # update meta data
        data = self.request(url=self._client.URL_METERS)
        if 'circuits' in data:
            for circuit in data['circuits']:
                if circuit['dsid'] == self._id:
                    self._data = circuit
                    break

        # update current consumption
        data = self.request(url=self.URL_POWER_CONSUMPTION, id=self._id)
        if 'consumption' in data:
            self._current_consumption = data['consumption']

        # update overall consumption
            data = self.request(url=self.URL_POWER_METER, id=self._id)
        if 'meterValue' in data:
            self._overall_consumption = data['meterValue']

    def get_current_consumption(self):
        """
        current energy consumption in watts

        :return: current consumption
        :rtype: int
        """
        return self._current_consumption

    def get_overall_consumption(self):
        """
        overall consumption as watt seconds

        :return: overall consumption
        :rtype: int
        """
        return self._overall_consumption
