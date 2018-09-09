# pydigitalstrom

Run bundled docker
```bash
$ docker-compose build

$ docker-compose up -d

$ docker-compose exec python bash
```

## Status

### Yellow (light) devices

*GE-KL, GE-KM*

Features: get status, turn on, turn off, toggle, identify, set brightness (if supported by device), update status

### Grey (blind) devices

*GR-KL*

Features: set position, get position, update status

### Black (joker) devices

*SW-ZWS (adaptor plug)*

Features: get status, turn on, turn off, toggle, update status

*SW-TKM (push button)*

Features: get status, update status

### Meter

Features: get metadata, get current power consumption, get overall power consumption, update data

### Scene

Features: turn on, turn off

## Example

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
