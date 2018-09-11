# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2018-09-11
### Added
- Test coverage increased
### Changed
- BREAKING - All things async
- Use aiohttp to make calls and provide api-using functions as async
- Comply with PEP8 formatting rules
- BREAKING merged DSTerminal and DSDevice into DSDevice
- BREAKING minimum required Python version is now 3.5.3
- Docker development environment now uses Python 3.6

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
