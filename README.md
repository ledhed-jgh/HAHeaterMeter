# HeaterMeter smoker controller component for Home Assistant
HeaterMeter smoker controller integration for HA.


## [BREAKING_CHANGES](./BREAKING_CHANGES.md)
## [CHANGELOG](./CHANGELOG.md)



## :heavy_check_mark: ToDo:
- [X] ~~Stop the integration from spamming the logs when the HeaterMeter is offline. (Thanks spoetnik)~~
- [X] Implement scan_interval.
- [-] ~~Make TEMP_FAHRENHEIT / TEMP_CELSIUS a user configurable option. or read it from the HeaterMeter config.~~
- [X] Home Assistant Discovery
- [X] Individual probe Hi/Lo alarms.
- [-] ~~Create service to enable/disable 'Ramp' mode.~~ (HeaterMeter API doesn't support this)
- [ ] Silence Alarm: Append a negative to the alarming probe's threshold temp (silencing the alarm) and after the specified period of time, remove the negative value (re-enable the alarm).
- [ ] StartUp Mode: When starting the smoker, slowly increment the setpoint until Probe0 reaches Target temp (Target = final desired setpoint). Once Target is reached, turn off RampUp. This will prevent the fan from running at 100% for long durations when you initially light the smoker causing more fuel to light than necessary.
- [ ] Ramp Mode: This will operate exactly like native [Ramp Mode](https://tvwbb.com/threads/introducing-ramp-mode-in-a-snapshot-near-you.61667/) within the HeaterMeter. "as your meat approaches doneness, the pit temperature will ramp down slowly so that when the meat is done, the pit is at the same temperature as the meat and therefore can "hold" indefinitely without overcooking". Unfortunately, there is no way to initiate 'Ramp Mode' from the API, so this will be implemented through the integration.
- [ ] Multi-Device Support: There are some out there that are fortunate enough to have more than one HeaterMeter, this feature will allow the integrationt to manage multiple HeaterMeter Devices within Home Assistant. The major challenge to this feature is that the API doesn't currently have a way to uniquely identify the HeaterMeter, so this feature will be on-hold until the API can perform this action See: [HeaterMeter #68](https://github.com/CapnBry/HeaterMeter/issues/68).
- [ ] Expose all HeaterMeter configuration options supported by the API through this integration.
  - [ ] PID Parameters [proportional, integral, derivative, bias]
  - [ ] Probe Type
  - [ ] Probe Naming
  - [ ] Probe Offsets (Calibration)
  - [ ] Probe Coefficients
  - [ ] LCD Backlight %
  - [ ] Lid Open Autodetect %
  - [ ] Lid Seconds
  - [ ] Lid Open Mode: Enable/Disable
  - [ ] Fan Speed Min
  - [ ] Fan Speed Max
  - [ ] Fan Active Floor
  - [ ] Fan Invert
  - [ ] Servo High
  - [ ] Servo Low
  - [ ] Servo Active Ceiling
  - [ ] Servo Invert
  - [ ] Toast Message




<br/>

## :bookmark_tabs: Table of Contents
- [Screenshots](#camera-screenshots)
- [Getting Started](#getting-started)
- [Example YAML](#home-assistant-examples)
	- [configuration.yaml](#configurationyaml)
	- [automation.yaml](#automationyaml)
	- [scripts.yaml](#scriptsyaml)
	- [ui-lovelace.yaml](#ui-lovelaceyaml)
- [References](#references)
<br/>

## :camera: Screenshots

## Lovelace Cards
![Lovelace Cards](docs/lovelace-cards-03.png)

### HeaterMeter Reference Image
![HeaterMeter Reference](docs/heatermeter-reference.png)

### Mobile App Notification
![Mobile App Notification](docs/mobile-app-notification.png)

### Mobile App Cards
![Mobile App Cards](docs/mobile-app-card-view.png)  
[:top:](#bookmark_tabs-table-of-contents)
<br/>
<br/>

## Getting started
* Copy the 'heatermeter' folder to the Home Assistant config/custom_components/ directory.  

[:top:](#bookmark_tabs-table-of-contents)
<br/>
<br/>

## Home Assistant Examples
### configuration.yaml
```yaml
heatermeter:
  api_key: <API Key from HeaterMeter>
  host: <Hostname or IP of HeaterMeter>
  port: 80
  scan_interval: <Time in seconds>  #(Not implemented yet)

input_number:
  setpoint:
    name: Setpoint
    initial: 225
    min:  100
    max:  400
    step: 1   
    mode: slider
    unit_of_measurement: "°F"
    icon: mdi:target
  probe0_hi:
    name: Probe0 Hi
    initial: 275
    min: -400
    max: 400
    step: 1
    mode: box
    unit_of_measurement: "°F"
    icon: mdi:target
  probe0_lo:
    name: Probe0 Lo
    initial: -200
    min: -400
    max: 400
    step: 1   
    mode: box
    unit_of_measurement: "°F"
    icon: mdi:target
  probe1_hi:
    name: Probe1 Hi
    initial: -200
    min: -400
    max: 400
    step: 1   
    mode: box
    unit_of_measurement: "°F"
    icon: mdi:target
  probe1_lo:
    name: Probe1 Lo
    initial: -1
    min: -400
    max: 400
    step: 1   
    mode: box
    unit_of_measurement: "°F"
    icon: mdi:target
  probe2_hi:
    name: Probe2 Hi
    initial: -200
    min: -400
    max: 400
    step: 1   
    mode: box
    unit_of_measurement: "°F"
    icon: mdi:target
  probe2_lo:
    name: Probe2 Lo
    initial: -1
    min: -400
    max: 400
    step: 1   
    mode: box
    unit_of_measurement: "°F"
    icon: mdi:target
  probe3_hi:
    name: Probe3 Hi
    initial: -200
    min: -400
    max: 400
    step: 1   
    mode: box
    unit_of_measurement: "°F"
    icon: mdi:target
  probe3_lo:
    name: Probe3 Lo
    initial: -1
    min: -400
    max: 400
    step: 1   
    mode: box
    unit_of_measurement: "°F"
    icon: mdi:target
```  
Notes:
* Set api_key:
* Set host:
* Change 'unit_of_measurement' to match your unit system.
* Optionally, Input Numbers can be created in the UI under 'Configuration\Helpers'. Make sure the names match.<br/>
[:top:](#bookmark_tabs-table-of-contents)
<br/>

### automation.yaml
```yaml
- id: 'heatermeter_push_notification'
  alias: HeaterMeter Push Notification
  description: ''
  trigger:
  - entity_id: heatermeter.alarm
    platform: state
    to: 'on'
  condition: []
  action:
  - data:
      data:
        actions:
        - action: URI
          title: Go to Card
          uri: /lovelace/heater-meter
      message: HeaterMeter Alarm
    service: notify.mobile_app_<YourPhone>
  mode: single
- id: 'bbq_is_ready'
  alias: BBQ is Ready
  description: ''
  trigger:
  - platform: template
    value_template: '{% if states(''heatermeter.probe1_temperature'') | int(0) > states(''heatermeter.probe1_hi'') | int(0) -1 %} true {% endif %}'
  condition:
  - condition: not
    conditions:
    - condition: state
      entity_id: heatermeter.probe1_temperature
      state: Unknown
  action:
  - service: tts.google_translate_say
    entity_id: media_player.living_room_speaker
    data:
      message: Your food is ready to come off the barbeque
  mode: single
- id: 'heatermeter_sync_alarm_values'
  alias: Update Heatermeater (No/Therm) Alarms
  description: Sync alarm values between HeaterMeter and Home Assistant.
  trigger:
  - platform: state
    entity_id:
    - heatermeter.probe0_hi
    - heatermeter.probe0_lo
    - heatermeter.probe1_hi
    - heatermeter.probe1_lo
    - heatermeter.probe2_hi
    - heatermeter.probe2_lo
    - heatermeter.probe3_hi
    - heatermeter.probe3_lo
  - platform: state
    entity_id: heatermeter.setpoint
    from: unknown
  condition: []
  action:
  - service: script.turn_on
    data:
      entity_id: script.update_heatermeter_input_numbers
  mode: single
```  
Notes:
* The 'tts.google_translate_say' service must be configured for the 'bbq_is_ready' automation to work and you should change the 'entity_id' to your desired media_player.
* Change 'service: notify.mobile_app_\<YourPhone\>' to match your notification service.<br/>
[:top:](#bookmark_tabs-table-of-contents)
<br/>
	
### scripts.yaml
```yaml
heatermeter_change_set_point:
  alias: HeaterMeter Change Set Point
  icon: mdi:target
  mode: single
  sequence:
  - data_template:
      temperature: '{{ states.input_number.setpoint.state|int(225) }}'
    service: heatermeter.set_temperature
update_heatermeter_input_numbers:
  alias: Update HeaterMeter Input Numbers
  sequence:
  - service: input_number.set_value
    data_template:
      value: '{{ states("heatermeter.probe0_hi") | int(-1) }}'
    entity_id: input_number.probe0_hi
  - service: input_number.set_value
    data_template:
      value: '{{ states("heatermeter.probe0_lo") | int(-1) }}'
    entity_id: input_number.probe0_lo
  - service: input_number.set_value
    data_template:
      value: '{{ states("heatermeter.probe1_hi") | int(-1) }}'
    entity_id: input_number.probe1_hi
  - service: input_number.set_value
    data_template:
      value: '{{ states("heatermeter.probe1_lo") | int(-1) }}'
    entity_id: input_number.probe1_lo
  - service: input_number.set_value
    data_template:
      value: '{{ states("heatermeter.probe2_hi") | int(-1) }}'
    entity_id: input_number.probe2_hi
  - service: input_number.set_value
    data_template:
      value: '{{ states("heatermeter.probe2_lo") | int(-1) }}'
    entity_id: input_number.probe2_lo
  - service: input_number.set_value
    data_template:
      value: '{{ states("heatermeter.probe3_hi") | int(-1) }}'
    entity_id: input_number.probe3_hi
  - service: input_number.set_value
    data_template:
      value: '{{ states("heatermeter.probe3_lo") | int(-1) }}'
    entity_id: input_number.probe3_lo
  mode: single
heatermeter_set_alarms:
  alias: HeaterMeter Set Alarms
  sequence:
  - service: heatermeter.set_alarms
    data_template:
      alarms: '{{ states("input_number.probe0_lo") }},{{ states("input_number.probe0_hi") }},{{ states("input_number.probe1_lo") }},{{ states("input_number.probe1_hi") }}",{{ states("input_number.probe2_lo") }},{{ states("input_number.probe2_hi") }},{{ states("input_number.probe3_lo") }},{{ states("input_number.probe3_hi") }}'
  mode: single
```  
Notes:
* In the 'heatermeter_change_set_point' script, change the data_template: temperature int(225) to natch your desired default set point. (This shouldn't be necessary as long as the corresponding input_number 'initial' value has been set)<br/>
[:top:](#bookmark_tabs-table-of-contents)
<br/>

### ui-lovelace.yaml
```yaml
  - icon: 'mdi:grill'
    path: heater-meter
    title: Heater Meter
    cards:
      - entities:
          - entity: input_number.setpoint
            name: 'New Set Point:'
          - action_name: Set
            icon: 'mdi:blank'
            name: ' '
            service: script.heatermeter_change_set_point
            type: call-service
        title: Change Set Point
        type: entities
      - entities:
          - entity: heatermeter.setpoint
          - entity: heatermeter.lid
          - entity: heatermeter.fan
          - entity: heatermeter.probe0_temperature
          - entity: heatermeter.probe1_temperature
            name: Food-1 Temperature
          - entity: heatermeter.probe2_temperature
            name: Food-2 Temperature
          - entity: heatermeter.probe3_temperature
            name: Ambient Temperature
          - entity: heatermeter.alarm
        show_header_toggle: false
        title: Smoker
        type: entities
      - entities:
          - entity: heatermeter.setpoint
          - entity: heatermeter.probe0_temperature
          - entity: heatermeter.probe1_temperature
          - entity: heatermeter.probe2_temperature
          - entity: heatermeter.probe3_temperature
          - entity: heatermeter.fan
        hours_to_show: 18
        refresh_interval: 10
        type: history-graph
      - entities:
          - type: section
            label: Pit
          - entity: input_number.probe0_hi
            name: 'Hi:'
          - entity: input_number.probe0_lo
            name: 'Lo:'
          - type: section
            label: Food-1
          - entity: input_number.probe1_hi
            name: 'Hi:'
          - entity: input_number.probe1_lo
            name: 'Lo:'
          - type: section
            label: Food-2
          - entity: input_number.probe2_hi
            name: 'Hi:'
          - entity: input_number.probe2_lo
            name: 'Lo:'
          - type: section
            label: Ambient
          - entity: input_number.probe3_hi
            name: 'Hi:'
          - entity: input_number.probe3_lo
            name: 'Lo:'
          - type: section
          - action_name: Set
            icon: 'mdi:blank'
            name: ' '
            service: script.heatermeter_set_alarms
            type: call-service
        title: Alarms
        type: entities
```  
[:top:](#bookmark_tabs-table-of-contents)
<br/>

## References
* Support for reading HeaterMeter data. See https://github.com/CapnBry/HeaterMeter/wiki/Accessing-Raw-Data-Remotely
* Home Assistant HeaterMeter integration forum post. https://community.home-assistant.io/t/heatermeter-integration/14696/22  
[:top:](#bookmark_tabs-table-of-contents)
