# -*- coding: UTF-8 -*-
import json
import os
import re
import time

import aiohttp

from pydigitalstrom.constants import SCENES
from pydigitalstrom.exceptions import DSException, DSCommandFailedException, \
    DSRequestException


class DSClient(object):
    URL_SERVER = '/json/system/version'
    URL_METERS = '/json/apartment/getCircuits'
    URL_DEVICES = '/json/apartment/getDevices'
    URL_ZONES_BY_METER = '/json/property/query?query=/apartment/dSMeters/' \
                         '*(name,dSID,dSUID,isValid)/zones/*(*)'
    URL_SCENES = '/json/property/query2?query=/apartment/zones/*(*)/' \
                 'groups/*/scenes/*(*)'

    URL_APPTOKEN = '/json/system/requestApplicationToken?applicationName=' \
                   'homeassistant'
    URL_TEMPTOKEN = '/json/system/login?user={username}&password={password}'
    URL_ACTIVATE = '/json/system/enableToken?applicationToken={apptoken}' \
                   '&token={temptoken}'
    URL_SESSIONTOKEN = '/json/system/loginApplication?loginToken={apptoken}'

    def __init__(self, host, username, password, config_path, apartment_name,
                 *args, **kwargs):
        self.host = host
        self.username = username
        self.password = password
        self._apartment_name = apartment_name

        self.config_path = config_path
        self._apptoken = None

        self._last_request = None
        self._session_id = None

        self._server = None
        self._meters = None
        self._apartment = None
        self._devices = None
        self._scenes = None
        super(DSClient).__init__(*args, **kwargs)

    async def get_application_token(self):
        if self._apptoken:
            return self._apptoken

        # try to load app token from config
        apptoken = None
        if os.path.isfile(self.config_path):
            with open(self.config_path, 'rt') as file:
                try:
                    config = json.loads(file.read())
                    if config and isinstance(config, dict) and \
                            'apptoken' in config:
                        apptoken = config['apptoken']
                except json.decoder.JSONDecodeError:
                    pass

        # try to validate app token
        if apptoken:
            try:
                await self.get_session_token(apptoken=apptoken)
                self._apptoken = apptoken
                return self._apptoken
            except DSException:
                pass

        # get fresh app token and activate it
        apptoken = await self.get_application_token_from_server()
        temptoken = await self.get_temp_token()
        await self.activate_application_token(
            apptoken=apptoken, temptoken=temptoken)

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

        self._apptoken = apptoken
        return self._apptoken

    async def raw_request(self, url: str, **kwargs):
        """
        run a raw request against the digitalstrom server

        :param str url: URL path to request
        :param dict kwargs: kwargs to be forwarded to aiohttp.get
        :return: json response
        :rtype; dict
        :raises: DSRequestException
        :raises: DSCommandFailedException
        """
        url = '{host}{path}'.format(host=self.host, path=url)

        # disable ssl verification for most servers miss valid certificates
        async with self.get_aiohttp_session() as session:
            try:
                async with session.get(url=url, **kwargs) as response:
                    # check for server errors
                    if not response.status == 200:
                        raise DSRequestException(response.text)

                    try:
                        data = await response.json()
                    except json.decoder.JSONDecodeError:
                        raise DSRequestException(
                            'failed to json decode response')
                    if 'ok' not in data or not data['ok']:
                        raise DSCommandFailedException()
                    return data
            except aiohttp.ClientError:
                raise DSRequestException('request failed')

    def get_aiohttp_session(self):
        return aiohttp.client.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False))

    async def request(self, url: str, check_result=True, **kwargs):
        """
        run an authenticated request against the digitalstrom server

        :param str url:
        :param bool check_result:
        :return:
        """
        # get a session id, they time out 60 seconds after the last request,
        # we go for 50 to be secure
        if not self._last_request or self._last_request < time.time() - 50:
            self._session_id = await self.get_session_token(
                await self.get_application_token())

        # update last request timestamp and call api
        self._last_request = time.time()
        data = await self.raw_request(
            url=url, params=dict(token=self._session_id), **kwargs)
        if check_result:
            if 'result' not in data:
                raise DSCommandFailedException('no result in server response')
            data = data['result']
        return data

    async def get_application_token_from_server(self):
        data = await self.raw_request(self.URL_APPTOKEN)
        if 'result' not in data or 'applicationToken' not in data['result']:
            raise DSException('invalid api response')
        return data['result']['applicationToken']

    async def get_temp_token(self):
        data = await self.raw_request(self.URL_TEMPTOKEN.format(
            username=self.username, password=self.password))
        if 'result' not in data or 'token' not in data['result']:
            raise DSException('invalid api response')
        return data['result']['token']

    async def activate_application_token(self, apptoken, temptoken):
        await self.raw_request(self.URL_ACTIVATE.format(
            apptoken=apptoken, temptoken=temptoken))
        return True

    async def get_session_token(self, apptoken):
        data = await self.raw_request(self.URL_SESSIONTOKEN.format(
            apptoken=apptoken))
        if 'result' not in data or 'token' not in data['result']:
            raise DSException('invalid api response')
        return data['result']['token']

    async def get_server(self):
        if not self._server:
            await self._initialize_server()
        return self._server

    async def _initialize_server(self):
        from pydigitalstrom.devices.server import DSServer

        data = await self.request(url=self.URL_SERVER)
        self._server = DSServer(client=self, data=data)

    async def get_meters(self):
        if self._meters is None:
            await self._initialize_meters()
        return self._meters.values()

    async def _initialize_meters(self):
        from pydigitalstrom.devices.meter import DSMeter

        self._meters = dict()

        data = await self.request(url=self.URL_METERS)
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

    async def get_scenes(self):
        if self._scenes is None:
            await self._initialize_scenes()
        return self._scenes.values()

    async def _initialize_scenes(self):
        from pydigitalstrom.devices.scene import DSScene

        self._scenes = dict()

        # get all zones by meter to skip ones only assigned to 3rd party meters
        ds_zones = []
        data = await self.request(url=self.URL_ZONES_BY_METER)
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
        data = await self.request(url=self.URL_SCENES)
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
                            zone_id=zone['ZoneID'], zone_name=zone_name,
                            scene_id=scene['scene'], scene_name=scene['name']))

            # add generic system scenes
            for scene_name, scene_id in SCENES.items():
                self._scenes['{zone}.{scene}'.format(
                    zone=zone['ZoneID'], scene=scene_id)] = DSScene(
                    client=self, data=dict(
                        zone_id=zone['ZoneID'], zone_name=zone_name,
                        scene_id=scene_id, scene_name=scene_name))

    async def get_devices(self):
        if self._devices is None:
            await self._initialize_devices()
        return self._devices

    async def _initialize_devices(self):
        from pydigitalstrom.devices.light import DSLight
        from pydigitalstrom.devices.blind import DSBlind
        from pydigitalstrom.devices.switch import DSSwitch, DSSwitchSensor

        self._devices = dict()

        data = await self.request(url=self.URL_DEVICES)
        for device in data:
            if not device['isValid'] or not device['isPresent']:
                continue

            matches = re.search(r'([A-Z]{2})-([A-Z]{2,3})(\d{3})(.*)',
                                device['hwInfo'])
            if not matches:
                continue

            device['hwColor'], device['hwFunction'], device['hwVersion'], _ = \
                matches.groups()

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
            if device['hwColor'] == 'GE' and \
                    device['hwFunction'] in ('KL', 'KM'):
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
                    self._devices[device['id']] = DSSwitch(
                        client=self, data=device)
                # TKM (push button - Tasterklemme M)
                if device['hwFunction'] == 'TKM':
                    self._devices[device['id']] = DSSwitchSensor(
                        client=self, data=device)

    async def get_devices_by_type(self, device_type):
        filtered_devices = []
        devices = await self.get_devices()
        for device in devices.values():
            if isinstance(device, device_type):
                filtered_devices.append(device)
        return filtered_devices

    async def get_lights(self):
        """
        get all light devices

        :return: light devices
        :rtype: List[:class:`DSLight`]
        """
        from pydigitalstrom.devices.light import DSLight
        return await self.get_devices_by_type(device_type=DSLight)

    async def get_blinds(self):
        """
        get all blind devices

        :return: blind devices
        :rtype: List[:class:`DSBlind`]
        """
        from pydigitalstrom.devices.blind import DSBlind
        return await self.get_devices_by_type(device_type=DSBlind)

    async def get_switches(self):
        """
        get all switch devices

        :return: switch devices
        :rtype: List[:class:`DSSwitch`]
        """
        from pydigitalstrom.devices.switch import DSSwitch
        return await self.get_devices_by_type(device_type=DSSwitch)

    async def get_switchsensors(self):
        """
        get all switch sensor devices

        :return: switch sensor devices
        :rtype: List[:class:`DSSwitchSensor`]
        """
        from pydigitalstrom.devices.switch import DSSwitchSensor
        return await self.get_devices_by_type(device_type=DSSwitchSensor)
