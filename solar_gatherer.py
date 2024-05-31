#!/usr/bin/env python3

import argparse
import configparser
import logging
import pysolarmanv5
import sys
import time

L = logging.getLogger(__name__)


class Gatherer():
    def __init__(self, path):
        # Read configuration
        config = configparser.ConfigParser()
        config.read(path)
        if "general" in config:
            self.DataStickIP = config["general"].get("inverter_ip")
            self.DataStickSerial = int(config["general"].get("inverter_serial"))
        else:
            L.warning("No 'general' section in config, using defaults")
            self.DataStickIP = "0.0.0.0"
            self.DataStickSerial = 123456789

        # Define registers (there are just 2 interesting ones at the moment, so not configurable)
        self.Registers = {
            "current_consumption": int(0x0485),
            "current_production": int(0x0586)
        }

    def gather_data(self):
        inverter_link = pysolarmanv5.PySolarmanV5(self.DataStickIP, self.DataStickSerial, port=8899)
        keep_asking = True
        failed_attempts = 0

        while keep_asking:
            try:
                current_consumption_kw = inverter_link.read_holding_registers(self.Registers["current_consumption"], 1)[0] * 0.01
                current_production_kw = inverter_link.read_holding_registers(self.Registers["current_production"], 1)[0] * 0.01
                print("Current consumption: {}\n".format(current_consumption_kw))
                print("Current production: {}\n".format(current_production_kw))
                keep_asking = False
            except Exception as e:
                L.warning("Exception while trying to reach inverter. Cause: {}.".format(e))
                failed_attempts += 1
                time.sleep(1)
                if failed_attempts > 15:
                    L.info("Too many attempts failed, giving up.")
                    keep_asking = False

if __name__ == "__main__":
    cmd_parser = argparse.ArgumentParser(description="Provide configuration path.")
    cmd_parser.add_argument("-c", "--config", type=str, required=True, help="Path to config file.")
    path = cmd_parser.parse_args()

    app = Gatherer(path.config)
    app.gather_data()
