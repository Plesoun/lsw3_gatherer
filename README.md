# Gatherer

Simple script to obtain current production, and current consumption from an LSW datastick (serial starting 23xxxxxx, firmware LSW3_15_270A_1.68) connected to an inverter.
Values are in kW.

## Configuration

Use a configuration file. Example:

`local.conf`

```
[inverter]
inverter_ip=197.16.125.120
inverter_serial=2335521351

[storage]
storage_ip=197.16.125.121
storage_port=5432
storage_db_name=mydb
storage_user=myuser
storage_password=mypass
```

## Building and running the script

This is intended to run in docker, so no requirements.txt provided, build the image while in the repo with:

`docker build -t gatherer .`

Run via:

`docker run --rm -v /your/configfile/location.conf:/conf/gatherer.conf gatherer`

remember, If you are using the storage, make sure it is accessible from the container, use `--network host` if needed
