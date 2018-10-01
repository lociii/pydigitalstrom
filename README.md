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

## Concept

Since digitalSTROM is mainly build on the concept of scenes, this library also only support setting scenes.

Currently user defined named scenes and generic scenes are supported.

## Example usage

```python
# -*- coding: UTF-8 -*-
import urllib3
import os

from pydigitalstrom.client import DSClient

# disable certificate warnings - dss uses self signed
async def test():
    urllib3.disable_warnings()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'auth.json')
    client = DSClient(host='https://dss.local:8080', username='dssadmin', password='mySuperSecretPassword',
                      config_path=config_path, apartment_name='Apartment')
    await client.initialize()
    scenes = client.get_scenes()
    for scene in scenes.values():
        print(scene.name)
        print(scene.unique_id)
        await scene.turn_on()
```
