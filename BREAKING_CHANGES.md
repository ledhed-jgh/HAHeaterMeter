# Breaking Changes

All notable breaking changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.2.0] - 2026-03-10

- All entity names will change due to the heatermeter domain being removed from the naming convention. The new naming convention is {device_type}.heatermeter_{name}. Unfortunately this will require updating existing automations and scripts.
    - Example, old: heatermeter.probe0_temp, new: sensor.heatermeter_probe_0_temp

- Renamed service/action heatermeter.set_temperature to heatermeter.new_setpoint, the old name wasn't clear it was setting a new setpoint. This change will require updating the service/action name in scripts, automations, Node-Red flows, etc...


## [0.1.0] - 2024-02-07

- The sensor previously reported "-" when an alarm was disabled, and the "update_heatermeter_input_numbers" script would update the alarm values in the UI to "-1". I've changed this behavior, and now the senor values match what is in heatermeter. You will need to update your "update_heatermeter_input_numbers" script accordingly. I've updated the example in the scripts.yaml section of this readme. The benefit to this is that those values in heatermeter survive a reboot, so if you always use the same alarm values, you can save them and just toggle them on/off by making the number negative. Example: Probe1 Alarm = 203, to disable the alarm (but retain the value) you can set it to -203. If you prefer the legacy -1 values to represent a disabled alarm, you can find an updated script in: "legacy_update_heatermeter_input_numbers.yaml"



### Release Reference
[unreleased]: https://github.com/ledhed-jgh/HAHeaterMeter
[0.2.0]: https://github.com/ledhed-jgh/HAHeaterMeter/releases/tag/v0.2.0-beta1
[0.1.0]: https://github.com/ledhed-jgh/HAHeaterMeter/releases/tag/v0.1.0
