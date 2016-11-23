# -*- coding: UTF-8 -*-
import requests
import logging

logger = logging.getLogger(__file__)


class DigitalStromAuthentication(object):
    URL_APPTOKEN = '%s/json/system/requestApplicationToken?applicationName=' \
                   'pydigitalstrom'
    URL_TEMPTOKEN = '%s/json/system/login?user=%s&password=%s'
    URL_ACTIVATE = '%s/json/system/enableToken?applicationToken=%s&token=%s'
    URL_SESSIONTOKEN = '%s/json/system/loginApplication?loginToken=%s'

    def __init__(self, address):
        self.address = address

    def getApplicationToken(self):
        json = self.request(self.URL_APPTOKEN % self.address)
        if 'ok' in json and json['ok']:
            return json['result']['applicationToken']
        return ''

    def getTempToken(self, username, password):
        json = self.request(self.URL_TEMPTOKEN % (self.address, username,
                                                  password))
        if 'ok' in json and json['ok']:
            return json['result']['token']
        return ''

    def activateApplicationToken(self, applicationtoken, temptoken):
        json = self.request(self.URL_ACTIVATE % (self.address, applicationtoken,
                                                 temptoken))
        if 'ok' in json and json['ok']:
            return True
        return False

    def getSessionToken(self, apptoken):
        json = self.request(self.URL_SESSIONTOKEN % (self.address, apptoken))
        if 'ok' not in json or not json['ok']:
            raise Exception('failed to get session token')
        return json['result']['token']

    def request(self, url):
        response = requests.get(url, verify=False)
        if not response.status_code == 200:
            raise Exception(response.text)
        return response.json()
