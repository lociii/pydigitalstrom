# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [0.6.1] - 2019-09-01
### Changed
- change the way ssl certificate validation is disabled

## [0.6.0] - 2019-09-01
### Changed
- BREAKING - app token will not be stored in a file anymore
- BREAKING - DSClient splitted into multiple classes, app token retrieval standalone
- updated python versions and dependencies
- format source code using black

## [0.5.0] - 2019-02-09
### Changed
- BREAKING - changed device unique_id to be underscore separated instead of dot separated
- updated python versions and dependencies

## [0.4.1] - 2018-10-01
### Changed
- Registering callbacks on the DSEventListener should not be async

## [0.4.0] - 2018-10-01
### Changed
- BREAKING - this library will only support scenes from now on since device actions suck on digitalSTROM!
- BREAKING - the DSEventListener will now forward event data to the callback instead of updating states on it's own

## [0.3.4] - 2018-09-30
### Added
- Update AreaBlind state from DSListener

## [0.3.3] - 2018-09-29
### Added
- Support for AreaBlind, basically converted scenes 0-9 to proper blind devices for the area

## [0.3.2] - 2018-09-16
### Changed
- Allow passing an asyncio loop to the DSListener

## [0.3.1] - 2018-09-16
### Added
- Support update callbacks on AreaLight

## [0.3.0] - 2018-09-16
### Added
- Support for AreaLight, basically converted scenes 0-9 to proper light devices for the area
- Event listener that can update the AreaLight status
### Changed
- BREAKING - devices etc are now initialized by DSClient.initialize() and DSClient getter functions are not async anymore

## [0.2.0] - 2018-09-11
### Added
- Test coverage increased
### Changed
- BREAKING - All things async
- Use aiohttp to make calls and provide api-using functions as async
- Comply with PEP8 formatting rules
- BREAKING merged DSTerminal and DSDevice into DSDevice
- BREAKING minimum required Python version is now 3.5.3
- Multi version Docker environment to run full tox suite

## [0.1.2] - 2018-09-10
### Fixed
- Some API calls should not expect a result node in response
### Changed
- Added more gitignores for docker env and app config

## [0.1.1] - 2018-09-10
### Added
- Tests for blind, light, meter and scene
- Add move_up, move_down and stop to blind
### Changed
- DSDevice and DSTerminal signature of request now allows for responses without result node

## [0.1.0] - 2018-09-09
### Changed
- Complete rewrite

### Added
- (yellow) Support for GE-KL200, GE-KM200
- (grey) Support for GR-KL200
- (black) Support for SW-ZW200-F, SW-TKM200
- (meter) Support for dSM12
- (server) Support for dSS IP
- Support for scenes

## [0.0.1] - 2016-11-23
### Added
- Initial release
