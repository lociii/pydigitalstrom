# -*- coding: UTF-8 -*-
from pydigitalstrom.client import DSClient

TEST_HOST = "https://dss.local:8080"
TEST_USERNAME = "dssadmin"
TEST_PASSWORD = "password"
TEST_TOKEN = "token"
TEST_APARTMENT = "Apartment"


def get_testclient(host=TEST_HOST, apptoken=TEST_TOKEN, apartment_name=TEST_APARTMENT):
    return DSClient(host=host, apptoken=apptoken, apartment_name=apartment_name)
