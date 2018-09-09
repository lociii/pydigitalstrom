[![PyPI version](https://badge.fury.io/py/pydigitalstrom.svg)](https://pypi.org/project/pydigitalstrom)
[![Travis CI build status](https://travis-ci.org/lociii/pydigitalstrom.svg)](https://travis-ci.org/lociii/pydigitalstrom)
[![Coverage Status](https://coveralls.io/repos/github/lociii/pydigitalstrom/badge.svg?branch=master)](https://coveralls.io/github/lociii/pydigitalstrom?branch=master)
[![MIT Licence](https://badges.frapsoft.com/os/mit/mit.svg?v=103)](https://opensource.org/licenses/mit-license.php)

# pydigitalstrom

Run bundled docker
```bash
$ docker-compose build

$ docker-compose up -d

$ docker-compose exec python bash
```

## Status

Tested devices

<table>
    <tr>
        <th>Device name</th>
        <th>Color group / device type</th>
        <th>Features</th>
    </tr>
    <tr>
        <td>GE-KL200</td>
        <td>Yellow (light)</td>
        <td>
            get status, turn on, turn off, toggle, identify, update status
        </td>
    </tr>
    <tr>
        <td>GE-KM200</td>
        <td>Yellow (light)</td>
        <td>
            get status, get brightness, turn on, turn off, toggle, identify, set brightness (if output mode permits), update status/brightness
        </td>
    </tr>
        <tr>
        <td>GR-KL200</td>
        <td>Grey (blinds)</td>
        <td>
            set position, get position, update position
        </td>
    </tr>
    </tr>
        <tr>
        <td>SW-ZW200-F</td>
        <td>Black (joker)</td>
        <td>
            (adaptor plug) get status, turn on, turn off, toggle, update status
        </td>
    </tr>
    </tr>
        <tr>
        <td>SW-TKM200</td>
        <td>Black (joker)</td>
        <td>
            (push button) get status, update status
        </td>
    </tr>
    </tr>
        <tr>
        <td>dSM12</td>
        <td>Meter</td>
        <td>
            get metadata, get current power consumption, get overall power consumption, update metadata/power consumption
        </td>
    </tr>
    </tr>
        <tr>
        <td>dSS IP</td>
        <td>Server</td>
        <td>
            get metadata, update metadata
        </td>
    </tr>
    </tr>
        <tr>
        <td>Scene</td>
        <td>Meta</td>
        <td>
            turn on, turn off
        </td>
    </tr>
</table>

## Example usage

```python
# -*- coding: UTF-8 -*-
import urllib3

from pydigitalstrom.client import DSClient

# disable certificate warnings - dss uses self signed
urllib3.disable_warnings()
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'auth.json')
client = DSClient(host='https://dss.local:8080', username='dssadmin', password='mySuperSecretPassword',
                  config_path=config_path, apartment_name='Apartment')
lights = client.get_lights()
for light in lights.values():
    print(light.name)
    print(light.unique_id)
    light.turn_on()
```
