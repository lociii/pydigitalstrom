# -*- coding: UTF-8 -*-
from pydigitalstrom.client import DSClient


def get_testclient(host='https://dss.local:8080', username='dssadmin',
                   password='password', config_path='/tmp',
                   apartment_name='Apartment'):
    return DSClient(host=host, username=username, password=password,
                    config_path=config_path, apartment_name=apartment_name)
