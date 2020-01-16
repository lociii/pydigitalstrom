# -*- coding: UTF-8 -*-
from pydigitalstrom.client import DSClient

TEST_HOST = "dss.local"
TEST_PORT = 8080
TEST_USERNAME = "dssadmin"
TEST_PASSWORD = "password"
TEST_TOKEN = "token"
TEST_APARTMENT = "Apartment"


def get_testclient(
    host=TEST_HOST, port=TEST_PORT, apptoken=TEST_TOKEN, apartment_name=TEST_APARTMENT
):
    return DSClient(
        host=host, port=port, apptoken=apptoken, apartment_name=apartment_name
    )
