# -*- coding: UTF-8 -*-
import time

from pydigitalstrom.constants import SCENE_NAMES
from pydigitalstrom.exceptions import (
    DSException,
    DSCommandFailedException,
    DSRequestException,
)
from pydigitalstrom.requesthandler import DSRequestHandler


class DSClient(DSRequestHandler):
    URL_SCENES = (
        "/json/property/query2?query=/apartment/zones/*(*)/" "groups/*(*)/scenes/*(*)"
    )
    URL_EVENT_SUBSCRIBE = "/json/event/subscribe?name={name}&" "subscriptionID={id}"
    URL_EVENT_UNSUBSCRIBE = "/json/event/unsubscribe?name={name}&" "subscriptionID={id}"
    URL_EVENT_POLL = "/json/event/get?subscriptionID={id}&timeout={timeout}"

    URL_SESSIONTOKEN = "/json/system/loginApplication?loginToken={apptoken}"

    def __init__(self, host, apptoken, apartment_name):
        self._apptoken = apptoken
        self._apartment_name = apartment_name

        self._last_request = None
        self._session_token = None
        self._scenes = dict()

        super().__init__(host=host)

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
            self._session_token = await self.get_session_token()

        # update last request timestamp and call api
        self._last_request = time.time()
        data = await self.raw_request(
            url=url, params=dict(token=self._session_token), **kwargs
        )
        if check_result:
            if "result" not in data:
                raise DSCommandFailedException("no result in server response")
            data = data["result"]
        return data

    async def get_session_token(self):
        data = await self.raw_request(
            self.URL_SESSIONTOKEN.format(apptoken=self._apptoken))
        if "result" not in data or "token" not in data["result"]:
            raise DSException("invalid api response")
        return data["result"]["token"]

    async def initialize(self):
        from pydigitalstrom.devices.scene import DSScene, DSColorScene

        # get scenes
        data = await self.request(url=self.URL_SCENES)

        # set name for apartment zone
        if "zone0" in data and "name" in data["zone0"]:
            data["zone0"]["name"] = self._apartment_name

        # create scene objects
        for zone in data.values():
            # skip unnamed zones
            if not zone["name"]:
                continue

            zone_id = zone["ZoneID"]
            zone_name = zone["name"]

            # add generic zone scenes
            for scene_id, scene_name in SCENE_NAMES.items():
                id = "{zone_id}_{scene_id}".format(zone_id=zone_id, scene_id=scene_id)
                self._scenes[id] = DSScene(
                    client=self,
                    zone_id=zone_id,
                    zone_name=zone_name,
                    scene_id=scene_id,
                    scene_name=scene_name,
                )

            # add area and custom named scenes
            for zone_key, zone_value in zone.items():
                # we're only interested in groups
                if not str(zone_key).startswith("group"):
                    continue

                # remember the color
                color = zone_value["color"]

                for group_key, group_value in zone_value.items():
                    # we're only interested in scenes
                    if not str(group_key).startswith("scene"):
                        continue

                    scene_id = group_value["scene"]
                    scene_name = group_value["name"]
                    id = "{zone_id}_{color}_{scene_id}".format(
                        zone_id=zone_id, color=color, scene_id=scene_id
                    )

                    self._scenes[id] = DSColorScene(
                        client=self,
                        zone_id=zone_id,
                        zone_name=zone_name,
                        scene_id=scene_id,
                        scene_name=scene_name,
                        color=color,
                    )

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
