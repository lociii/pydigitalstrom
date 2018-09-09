from pydigitalstrom.client import DSClient


def get_testclient():
    return DSClient(host='https://dss.local:8080', username='dssadmin', password='password',
                    config_path='/tmp', apartment_name='Apartment')
