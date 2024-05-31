#!/usr/bin/env python3

import argparse
import configparser
import logging
import psycopg2
import pysolarmanv5
import sys
import time

L = logging.getLogger(__name__)


class Gatherer():
    def __init__(self, path):
        # Read configuration
        config = configparser.ConfigParser()
        config.read(path)
        # Inverter configuration
        if "inverter" in config:
            self.DataStickIP = config["inverter"].get("inverter_ip")
            self.DataStickSerial = int(config["general"].get("inverter_serial"))
        else:
            L.warning("No 'general' section in config, using defaults")
            self.DataStickIP = "0.0.0.0"
            self.DataStickSerial = 123456789

        # Database configuration
        if "storage" in config:
            self.DBHost = config["storage"].get("storage_ip")
            self.DBPort = config["storage"].get("storage_port")
            self.DBUser = config["storage"].get("storage_user")
            self.DBName =config["storage"].get("storage_db_name")
            self.DBPassword = config["storage"].get("storage_password")

        L.info(
            "Datastick configuration:\n stick_ip={stick_ip}\n stick_serial={stick_serial}".format(
                stick_ip=self.DataStickIP, stick_serial=self.DataStickSerial
            )
        )

        L.info(
            "Storage configuration:\n db_name={db_name}\n user={db_user}\n password=****\n host={db_host}\n port={db_port}".format(
                db_name=self.DBName, db_user=self.DBUser, db_host=self.DBHost, db_port=self.DBPort
            )
        )

        # Define registers (there are just 2 interesting ones at the moment, so not configurable)
        self.Registers = {
            "power_consumption": int(0x0485),
            "power_production": int(0x0586)
        }

    def gather_data(self):
        inverter_link = pysolarmanv5.PySolarmanV5(self.DataStickIP, self.DataStickSerial, port=8899)
        keep_asking = True
        failed_attempts = 0

        while keep_asking:
            try:
                power_consumption_kw = inverter_link.read_holding_registers(self.Registers["power_consumption"], 1)[0] * 0.01
                power_production_kw = inverter_link.read_holding_registers(self.Registers["power_production"], 1)[0] * 0.01
                print("Current consumption: {}\n".format(power_consumption_kw))
                print("Current production: {}\n".format(power_production_kw))
                keep_asking = False
            except Exception as e:
                L.warning("Exception while trying to reach inverter. Cause: {}.".format(e))
                failed_attempts += 1
                time.sleep(1)
                if failed_attempts > 15:
                    L.info("Too many attempts failed, giving up.")
                    keep_asking = False

    def write_data(self):
        with psycopg2.connect("dbname={db_name} user={dbuser}") as connection:
            pass

if __name__ == "__main__":
    cmd_parser = argparse.ArgumentParser(description="Provide configuration path.")
    cmd_parser.add_argument("-c", "--config", type=str, required=True, help="Path to config file.")
    path = cmd_parser.parse_args()

    app = Gatherer(path.config)
    app.gather_data()
