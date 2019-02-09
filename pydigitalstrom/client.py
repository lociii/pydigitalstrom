# -*- coding: UTF-8 -*-
import json
import os
import time

import aiohttp

from pydigitalstrom.constants import SCENE_NAMES
from pydigitalstrom.exceptions import DSException, DSCommandFailedException, \
    DSRequestException


class DSClient(object):
    URL_SCENES = '/json/property/query2?query=/apartment/zones/*(*)/' \
                 'groups/*(*)/scenes/*(*)'
    URL_EVENT_SUBSCRIBE = '/json/event/subscribe?name={name}&' \
                          'subscriptionID={id}'
    URL_EVENT_UNSUBSCRIBE = '/json/event/unsubscribe?name={name}&' \
                            'subscriptionID={id}'
    URL_EVENT_POLL = '/json/event/get?subscriptionID={id}&timeout={timeout}'

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
        self._scenes = dict()

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
        async with await self.get_aiohttp_session() as session:
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

    async def get_aiohttp_session(self):
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

    async def initialize(self):
        from pydigitalstrom.devices.scene import DSScene, DSColorScene

        # get scenes
        data = await self.request(url=self.URL_SCENES)

        # set name for apartment zone
        if 'zone0' in data and 'name' in data['zone0']:
            data['zone0']['name'] = self._apartment_name

        # create scene objects
        for zone in data.values():
            # skip unnamed zones
            if not zone['name']:
                continue

            zone_id = zone['ZoneID']
            zone_name = zone['name']

            # add generic zone scenes
            for scene_id, scene_name in SCENE_NAMES.items():
                id = '{zone_id}_{scene_id}'.format(
                    zone_id=zone_id, scene_id=scene_id)
                self._scenes[id] = DSScene(
                    client=self, zone_id=zone_id, zone_name=zone_name,
                    scene_id=scene_id, scene_name=scene_name)

            # add area and custom named scenes
            for zone_key, zone_value in zone.items():
                # we're only interested in groups
                if not str(zone_key).startswith('group'):
                    continue

                # remember the color
                color = zone_value['color']

                for group_key, group_value in zone_value.items():
                    # we're only interested in scenes
                    if not str(group_key).startswith('scene'):
                        continue

                    scene_id = group_value['scene']
                    scene_name = group_value['name']
                    id = '{zone_id}_{color}_{scene_id}'.format(
                        zone_id=zone_id, color=color, scene_id=scene_id)

                    self._scenes[id] = DSColorScene(
                        client=self, zone_id=zone_id, zone_name=zone_name,
                        scene_id=scene_id, scene_name=scene_name, color=color)

    def get_scenes(self):
        return self._scenes

    async def event_subscribe(self, event_id, event_name):
        """
        subscribe to an event for event_poll

        :param int event_id: id of the event
        :param str event_name: name of the event
        :return: success state
        :rtype: bool
        :raises DSRequestException: on request failure
        """
        url = self.URL_EVENT_SUBSCRIBE.format(name=event_name, id=event_id)
        await self.request(url, check_result=False)
        return True

    async def event_unsubscribe(self, event_id, event_name):
        """
        unsubscribe from an event for event_poll

        :param int event_id: id of the event
        :param str event_name: name of the event
        :return: success state
        :rtype: bool
        :raises DSRequestException: on request failure
        """
        url = self.URL_EVENT_UNSUBSCRIBE.format(name=event_name, id=event_id)
        await self.request(url, check_result=False)
        return True

    async def event_poll(self, event_id, timeout):
        """
        poll for actions on an event

        :param int event_id: id of the event
        :param int timeout: timeout in ms
        :return: event data
        :rtype: dict
        :raises DSRequestException: on request failure
        """
        url = self.URL_EVENT_POLL.format(id=event_id, timeout=timeout * 1000)
        return await self.request(url)
