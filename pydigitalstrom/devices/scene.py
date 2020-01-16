# -*- coding: UTF-8 -*-
from pydigitalstrom.client import DSClient
from pydigitalstrom.devices.base import DSDevice


class DSScene(DSDevice):
    URL_TURN_ON = (
        "/json/zone/callScene?id={zone_id}&" "sceneNumber={scene_id}&force=true"
    )

    def __init__(
        self,
        client: DSClient,
        zone_id,
        zone_name,
        scene_id,
        scene_name,
        *args,
        **kwargs
    ):
        self.zone_id = zone_id
        self.zone_name = zone_name
        self.scene_id = scene_id
        self.scene_name = scene_name

        device_id = "{zone_id}_{scene_id}".format(
            zone_id=self.zone_id, scene_id=self.scene_id
        )
        device_name = "{zone} / {name}".format(
            zone=self.zone_name, name=self.scene_name
        )

        super().__init__(
            client=client, device_id=device_id, device_name=device_name, *args, **kwargs
        )

    async def turn_on(self):
        await self.request(
            url=self.URL_TURN_ON.format(zone_id=self.zone_id, scene_id=self.scene_id)
        )


class DSColorScene(DSDevice):
    URL_TURN_ON = (
        "/json/zone/callScene?id={zone_id}&"
        "sceneNumber={scene_id}&groupID={color}&force=true"
    )

    def __init__(
        self,
        client: DSClient,
        zone_id,
        zone_name,
        scene_id,
        scene_name,
        color,
        *args,
        **kwargs
    ):
        self.zone_id = zone_id
        self.zone_name = zone_name
        self.scene_id = scene_id
        self.scene_name = scene_name
        self.color = color

        device_id = "{zone_id}_{color}_{scene_id}".format(
            zone_id=self.zone_id, color=self.color, scene_id=self.scene_id
        )
        device_name = "{zone} / {name}".format(
            zone=self.zone_name, name=self.scene_name
        )

        super().__init__(
            client=client, device_id=device_id, device_name=device_name, *args, **kwargs
        )

    async def turn_on(self):
        await self.request(
            url=self.URL_TURN_ON.format(
                zone_id=self.zone_id, color=self.color, scene_id=self.scene_id
            )
        )
