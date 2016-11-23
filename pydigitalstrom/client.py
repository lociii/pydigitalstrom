# -*- coding: UTF-8 -*-
import requests, logging
import time

from authorization import DigitalStromAuthentication

logger = logging.getLogger(__file__)


class DigitalStromClient(object):
    URL_GET_SCENES = '%s/json/zone/getReachableScenes'
    URL_GET_DEVICES = '%s/json/apartment/getStructure'

    def __init__(self, server):
        self.server = server
        self.session_id = None
        self.last_request = None

    def get_devices(self):
        json = self.request(self.URL_GET_DEVICES % self.server.address)
        if 'ok' not in json or not json['ok']:
            return False

    def request(self, url):
        # get a session id
        if not self.last_request or self.last_request < time.time() - 60:
            self.session_id = DigitalStromAuthentication(
                self.server.address).getSessionToken(self.server.apptoken)

        # update last request timestamp and call api
        self.last_request = time.time()
        response = requests.get(url, params=dict(token=self.session_id),
                                verify=False)
        logger.error(response.status_code)
        logger.error(response.text)
        return response.json()
