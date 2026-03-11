# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).



## [v0.2.0] - 2026-03-10

### Added

- CHANGELOG.md file to hopefully serve as an evolving example of a standardized open source project CHANGELOG.
- BREAKING_CHANGES.md to make README.md more concise. 
- Added a Config_Flow so the integration is now setup through the HA UI, no more YAML.
- Setpoint and Alarms are now synchronized with the HeaterMeter automatically. No need to create a script to call a service to push values. Just enter the value you want for a Setpoint and it gets pushed the HeaterMeter automatically. Conversely, changes made directly on the HeaterMeter (with physical buttons or the WebUI) are automatically pushed back to the Integration.
- All entities created by this integration are now added to a HeaterMeter device. So now you can conveniently access them from the Integrations tab.
- Added a clickable link to the HeaterMeter's WebUI from Device Info.
- Improved logging so changes are reflected in the Device's Activity log.
- Lid binary_sensor now has an attribute called "seconds_remaining".

* Alarm binary_sensor now has two new attributes:
    * Now includes a card for setting the Set Point with a slider and 'Set' button.
    * probe_name: displays the Friendly Name of the probe that is alarming.
    * These attributes facilitate creating more complex automations.

* New service 'heatermeter.set_alarm_by_index' to facilitate synchronizing single value changes. Note: service 'heatermeter.set_alarms' still exists for backwards compatibility or in scenarios where you want to push all alarm values at once in a script, automation, or Node-Red flow.
    * Example: you have presets for Pork Butt, Brisket, Chicken, etc...

- Discovery/ZeroConf, so newly discovered HeaterMeters will show up in the Discovered section of the Integrations tab.
- Improved device availability. When the HeaterMeter goes offline, all entities enter the Unavailable state. The byproduct of this is less spam in the logs.

### Fixed

- Migraged code base to Async logic required by Home Assistant.
- Helpers interface change in HomeAsstiant 2024+ breaks component [#9]


### Changed

- Migrated Setpoint and Alarm sensors to NumberEntity, removing the need to manually create Input_Number Helpers.

### Removed

- Need for Input_Number Helpers used to set Alarm values and Setpoint.
- Dependency on scripts used in the legacy integration for setting and/or retrieving alarm values and setpoint.



## [v0.1.0] - 2023-03-10

### Added

- Negative Alarm values are sync'd (rather than displaying -1).
- 'Update HeaterMeter Alarms' automation (Contributed by Chris8837).
- 'heatermeter.set_alarms' and 'heatermeter.set_temperature' scripts for setting & refreshing alarms.
- 'Alarms' card to ui-lovalace.yaml.
- 'automation.bbq_is_ready' automation to announce when your food is ready.
- High/Low Alarm Sensors for each probe.
- 'set_alarms' service to set probe alarms.
- Temperature units automatically set based on 'Unit System' setting in 'Configuration\General'.
- Alarm sensor that changes to 'on' when any probe's Alarm/Ring value is set to a non-null value.
- Automation example to send push notifications w/ action to mobile app.
- Lovelace Card Updates:
    - Now includes a card for setting the Set Point with a slider and 'Set' button.
    - Added history graph for the fan.

### Fixed

- Fixed depreciated constants (TEMP_CELSIUS/TEMP_FAHRENHEIT) to UnitOfTemperature
    - (legacy constants to be removed in 2025.1)
- Fixed Issue #1 'Fill Example Data inserts parameter twice', removed parameter from service example.


### Changed

- YAML to include default values for INT and FLOAT values in templates.
    - See [2021.10 Breaking Changes\Templates]
- Lid icon to mdi:room-service because it looks more like a BBQ lid.
- Input_Number's icon to mdi:target.
- Default heatermeter.set_temperature to 225.
- Changed script.yaml by removing the trigger. (Set Point will be set manually in the Lovelace card).

### Removed

- Username and password configuration options, use api_key instead.
- Refresh button from Alarms card (not needed with the sync alarms automation).


<!-- ### Link References -->
[unreleased]: https://github.com/ledhed-jgh/HAHeaterMeter
[v0.2.0]: https://github.com/ledhed-jgh/HAHeaterMeter/releases/tag/v0.2.0-beta1
[v0.1.0]: https://github.com/ledhed-jgh/HAHeaterMeter/releases/tag/v0.1.0
[#9]: https://github.com/ledhed-jgh/HAHeaterMeter/issues?q=is%3Aissue%20state%3Aclosed
[2021.10 Breaking Changes\Templates]: https://www.home-assistant.io/blog/2021/10/06/release-202110/#breaking-changes


<!-- ### Template

## [v0.0.0] - 2026-01-01

### Added

- 

### Changed

- 

### Removed

- 

-->

