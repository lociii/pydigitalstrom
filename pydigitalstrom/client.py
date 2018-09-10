# -*- coding: UTF-8 -*-
import json
import os
import re
import time

import requests

from pydigitalstrom.constants import SCENES
from pydigitalstrom.exceptions import DSException, DSCommandFailedException, DSRequestException


class DSClient(object):
    URL_SERVER = '/json/system/version'
    URL_METERS = '/json/apartment/getCircuits'
    URL_DEVICES = '/json/apartment/getDevices'
    URL_ZONES_BY_METER = '/json/property/query?query=/apartment/dSMeters/*(name,dSID,dSUID,isValid)/zones/*(*)'
    URL_SCENES = '/json/property/query2?query=/apartment/zones/*(*)/groups/*/scenes/*(*)'

    URL_APPTOKEN = '/json/system/requestApplicationToken?applicationName=homeassistant'
    URL_TEMPTOKEN = '/json/system/login?user={username}&password={password}'
    URL_ACTIVATE = '/json/system/enableToken?applicationToken={apptoken}&token={temptoken}'
    URL_SESSIONTOKEN = '/json/system/loginApplication?loginToken={apptoken}'

    def __init__(self, host, username, password, config_path, apartment_name, *args, **kwargs):
        self.host = host
        self.username = username
        self.password = password
        self._apartment_name = apartment_name

        self.config_path = config_path
        self.apptoken = None

        self.last_request = None
        self.session_id = None

        self._server = None
        self._meters = None
        self._apartment = None
        self._devices = None
        self._scenes = None
        super(DSClient).__init__(*args, **kwargs)

    def get_application_token(self):
        if self.apptoken:
            return self.apptoken

        # try to load app token from config
        apptoken = None
        if os.path.isfile(self.config_path):
            with open(self.config_path, 'rt') as file:
                config = json.loads(file.read())
                if config and isinstance(config, dict) and 'apptoken' in config:
                    apptoken = config['apptoken']

        # try to validate app token
        if apptoken:
            try:
                self.get_session_token(apptoken=apptoken)
                self.apptoken = apptoken
                return self.apptoken
            except DSException:
                pass

        # get fresh app token and activate it
        apptoken = self.get_application_token_from_server()
        temptoken = self.get_temp_token()
        self.activate_application_token(apptoken=apptoken, temptoken=temptoken)

        # make sure our config directory exists
        config_dir = os.path.dirname(self.config_path)
        if not os.path.isdir(config_dir):
            try:
                os.mkdir(config_dir)
            except Exception:
                raise DSException('config dir is not writable')

        # save app token in module config
        with open(self.config_path, 'wt') as file:
            file.write(json.dumps(dict(apptoken=apptoken)))

        self.apptoken = apptoken
        return self.apptoken

    def raw_request(self, url: str, **kwargs):
        """
        run a raw request against the digitalstrom server

        :param str url: URL path to request
        :param dict kwargs: kwargs to be forwarded to requests.get
        :return: json response
        :rtype; dict
        :raises: DSRequestException
        :raises: DSCommandFailedException
        """
        url = '{host}{path}'.format(host=self.host, path=url)

        try:
            response = requests.get(url=url, verify=False, **kwargs)
        except Exception:
            raise DSRequestException('request failed')
        if not response.status_code == 200:
            raise DSRequestException(response.text)

        try:
            data = response.json()
        except Exception:
            raise DSRequestException('invalid json received')

        if 'ok' not in data or not data['ok']:
            raise DSCommandFailedException()

        return data

    def request(self, url: str, check_result=True, **kwargs):
        """
        run an authenticated request against the digitalstrom server

        :param str url:
        :param bool check_result:
        :return:
        """
        # get a session id, they time out 60 seconds after the last request, we go for 50 to be secure
        if not self.last_request or self.last_request < time.time() - 50:
            self.session_id = self.get_session_token(self.get_application_token())

        # update last request timestamp and call api
        self.last_request = time.time()
        data = self.raw_request(url=url, params=dict(token=self.session_id), **kwargs)
        if check_result:
            if 'result' not in data:
                raise DSCommandFailedException('no result in server response')
            data = data['result']
        return data

    def get_application_token_from_server(self):
        data = self.raw_request(self.URL_APPTOKEN)
        if 'result' not in data or 'applicationToken' not in data['result']:
            raise DSException('invalid api response')
        return data['result']['applicationToken']

    def get_temp_token(self):
        data = self.raw_request(self.URL_TEMPTOKEN.format(
            username=self.username, password=self.password))
        if 'result' not in data or 'token' not in data['result']:
            raise DSException('invalid api response')
        return data['result']['token']

    def activate_application_token(self, apptoken, temptoken):
        self.raw_request(self.URL_ACTIVATE.format(
            apptoken=apptoken, temptoken=temptoken))
        return True

    def get_session_token(self, apptoken):
        data = self.raw_request(self.URL_SESSIONTOKEN.format(
            apptoken=apptoken))
        return data['result']['token']

    def get_server(self):
        if not self._server:
            self._initialize_server()
        return self._server

    def _initialize_server(self):
        from pydigitalstrom.devices.server import DSServer

        data = self.request(url=self.URL_SERVER)
        self._server = DSServer(client=self, data=data)

    def get_meters(self):
        if self._meters is None:
            self._initialize_meters()
        return self._meters

    def _initialize_meters(self):
        from pydigitalstrom.devices.meter import DSMeter

        self._meters = dict()

        data = self.request(url=self.URL_METERS)
        if 'circuits' not in data:
            return

        for circuit in data['circuits']:
            # skip virtual devices
            if 'dspSwVersion' in circuit and circuit['dspSwVersion'] == 0:
                continue
            # only valid entries
            if not circuit['isValid'] or not circuit['isPresent']:
                continue
            self._meters[circuit['dsid']] = DSMeter(client=self, data=circuit)

    def get_scenes(self):
        if self._scenes is None:
            self._initialize_scenes()
        return self._scenes

    def _initialize_scenes(self):
        from pydigitalstrom.devices.scene import DSScene

        self._scenes = dict()

        # get all zones by meter to skip ones only assigned to 3rd party meters
        ds_zones = []
        data = self.request(url=self.URL_ZONES_BY_METER)
        if 'dSMeters' in data:
            for meter in data['dSMeters']:
                # skip 3rd party meters
                if meter['dSID'] == '':
                    continue

                if 'zones' in meter:
                    for zone in meter['zones']:
                        ds_zones.append(zone['ZoneID'])
        ds_zones = list(set(ds_zones))

        # get scenes
        data = self.request(url=self.URL_SCENES)
        for zone in data.values():
            # skip zones only available to 3rd party meters
            if zone['ZoneID'] not in ds_zones:
                continue

            # apartment zone has no name, use provided default
            zone_name = zone['name']
            if zone['ZoneID'] == 0:
                zone_name = self._apartment_name

            # add zone specific scenes
            for key, scene in zone.items():
                if key.startswith('scene'):
                    self._scenes['{zone}.{scene}'.format(
                        zone=zone['ZoneID'], scene=scene['scene'])] = DSScene(
                        client=self, data=dict(
                            zone_id=zone['ZoneID'], scene_id=scene['scene'],
                            name=scene['name'], zone_name=zone_name))

            # add generic system scenes
            for scene_name, scene_id in SCENES.items():
                self._scenes['{zone}.{scene}'.format(
                    zone=zone['ZoneID'], scene=scene_id)] = DSScene(
                    client=self, data=dict(
                        zone_id=zone['ZoneID'], scene_id=scene_id,
                        name=scene_name, zone_name=zone_name))

    def get_devices(self):
        if self._devices is None:
            self._initialize_devices()
        return self._devices

    def _initialize_devices(self):
        from pydigitalstrom.devices.light import DSLight
        from pydigitalstrom.devices.blind import DSBlind
        from pydigitalstrom.devices.switch import DSSwitch, DSSwitchSensor

        self._devices = dict()

        data = self.request(url=self.URL_DEVICES)
        for device in data:
            if not device['isValid'] or not device['isPresent']:
                continue

            matches = re.search(r'([A-Z]{2})-([A-Z]{2,3})(\d{3})(.*)', device['hwInfo'])
            if not matches:
                continue

            device['hwColor'], device['hwFunction'], device['hwVersion'], rubbish = matches.groups()

            """
            GE = Gelb
            GR = Grau
            SW = Schwarz
            BL = Blau
            GN = Gruen

            KL = Klemme L
            KM = Klemme M
            TKM = Taster Klemme M
            SDM = Schnurdimmer M
            SDS = Schnurdimmer S
            UMV = Universal Modul Volt
            UMR = Universal Modul Relais
            AKM - Automatisierungsklemme
            ZWS = Zwischenstecker
            """

            # light (yellow group, GE => gelb)
            # TODO support TKM, push button and light mixed devices
            if device['hwColor'] == 'GE' and device['hwFunction'] in ('KL', 'KM'):
                self._devices[device['id']] = DSLight(client=self, data=device)

            # blinds (gray group, GR => grau)
            # TODO support TKM, push button and blind mixed devices
            if device['hwColor'] == 'GR' and device['hwFunction'] == 'KL':
                self._devices[device['id']] = DSBlind(client=self, data=device)

            # joker (black group, SW => schwarz)
            # TODO support AKM, automation sensor (Automatisierungsklemme)
            if device['hwColor'] == 'SW':
                # ZWS (adapter plug - Zwischenstecker)
                if device['hwFunction'] == 'ZWS':
                    self._devices[device['id']] = DSSwitch(client=self, data=device)
                # TKM (push button - Tasterklemme M)
                if device['hwFunction'] == 'TKM':
                    self._devices[device['id']] = DSSwitchSensor(client=self, data=device)

    def get_lights(self):
        """
        get all light devices

        :return: light devices
        :rtype: Iterator[:class:`DSLight`]
        """
        from pydigitalstrom.devices.light import DSLight

        for device in self.get_devices().values():
            if isinstance(device, DSLight):
                yield device

    def get_blinds(self):
        """
        get all blind devices

        :return: blind devices
        :rtype: Iterator[:class:`DSBlind`]
        """
        from pydigitalstrom.devices.blind import DSBlind

        for device in self.get_devices().values():
            if isinstance(device, DSBlind):
                yield device

    def get_switches(self):
        """
        get all switch devices

        :return: switch devices
        :rtype: Iterator[:class:`DSSwitch`]
        """
        from pydigitalstrom.devices.switch import DSSwitch

        for device in self.get_devices().values():
            if isinstance(device, DSSwitch):
                yield device

    def get_switchsensors(self):
        """
        get all switch sensor devices

        :return: switch sensor devices
        :rtype: Iterator[:class:`DSSwitchSensor`]
        """
        from pydigitalstrom.devices.switch import DSSwitchSensor

        for device in self.get_devices().values():
            if isinstance(device, DSSwitchSensor):
                yield device
