# Gatherer

Simple script to obtain current production, and current consumption from an LSW datastick (serial starting 23xxxxxx, firmware LSW3_15_270A_1.68) connected to an inverter.
Values are in kW.

## Configuration

Use a configuration file. Example:

`local.conf`

```
[general]
inverter_ip=197.16.125.120
inverter_serial=2335521351
```

## Building and running the script

This is intended to run in docker, so no requirements.txt provided, build the image while in the repo with:

`docker build -t gatherer .`

Run via

`docker run -v /your/configfile/location:/conf gatherer`
