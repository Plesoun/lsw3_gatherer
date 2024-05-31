#!/usr/bin/env python3

import argparse
import configparser
import datetime
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
            self.DataStickSerial = int(config["inverter"].get("inverter_serial"))
        else:
            L.warning("No 'inverter' section in config, using defaults")
            self.DataStickIP = "0.0.0.0"
            self.DataStickSerial = 123456789

        # Database configuration
        if "storage" in config:
            self.DBConnInfo = {
                'dbname': config["storage"].get("storage_db_name"),
                'user': config["storage"].get("storage_user"),
                'password': config["storage"].get("storage_password"),
                'host': config["storage"].get("storage_ip"),
                'port': config["storage"].get("storage_port"),
            }

        L.info(
            "Datastick configuration:\n stick_ip={stick_ip}\n stick_serial={stick_serial}".format(
                stick_ip=self.DataStickIP, stick_serial=self.DataStickSerial
            )
        )

        L.info(
            "Storage configuration:\n{db_info}".format(
                db_info=self.DBConnInfo,
            )
        )

        # Define registers (there are just 2 interesting ones at the moment, so not configurable)
        self.Registers = {
            "power_consumption": int(0x0485),
            "power_production": int(0x0586)
        }

    def gather_data(self) -> dict:
        inverter_link = pysolarmanv5.PySolarmanV5(self.DataStickIP, self.DataStickSerial, port=8899)
        keep_asking = True
        failed_attempts = 0

        while keep_asking:
            try:
                power_consumption_kw = inverter_link.read_holding_registers(self.Registers["power_consumption"], 14)[13] * 0.01
                power_production_kw = inverter_link.read_holding_registers(self.Registers["power_production"], 1)[0] * 0.01

                data = {
                    "timestamp": int(datetime.datetime.utcnow().timestamp()),
                    "power_consumption": power_consumption_kw,
                    "power_production": power_production_kw
                }
                L.info("Current consumption: {}\n".format(data["timestamp"]))
                L.info("Current production: {}\n".format(data["power_consumption"]))
                keep_asking = False
            except Exception as e:
                L.warning("Exception while trying to reach inverter. Cause: {}.".format(e))
                failed_attempts += 1
                time.sleep(1)
                if failed_attempts > 15:
                    L.info("Too many attempts failed, giving up.")
                    keep_asking = False
        return data

    def write_data(self):
        data_to_insert = self.gather_data()
        with psycopg2.connect(**self.DBConnInfo) as connection:
            with connection.cursor() as cursor:
                try:
                    insert_query = """
                    INSERT INTO power_data (timestamp, power_consumption, power_production)
                    VALUES (%s, %s, %s)
                    """
                    cursor.execute(insert_query, (data_to_insert["timestamp"], data_to_insert["power_consumption"], data_to_insert["power_production"]))
                    connection.commit()
                    L.info("Data inserted successfully.")
                except (Exception, psycopg2.DatabaseError) as e:
                    L.error("Error while trying to insert data: {}".format(e))
                    connection.rollback()


        # Connection is not closed by the context https://www.psycopg.org/docs/connection.html
        connection.close()


if __name__ == "__main__":
    cmd_parser = argparse.ArgumentParser(description="Provide configuration path.")
    cmd_parser.add_argument("-c", "--config", type=str, required=True, help="Path to config file.")
    path = cmd_parser.parse_args()

    app = Gatherer(path.config)
    app.write_data()
