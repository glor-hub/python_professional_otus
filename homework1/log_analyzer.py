#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

import os
import argparse
import configparser
from collections import namedtuple

default_config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

DEFAULT_CONFIG_FILE_PATH = os.path.abspath('config.ini')

LastLogFile=namedtuple('LastLogFile', ['path', 'ext', 'date'])

def get_config_path():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config',
        default=DEFAULT_CONFIG_FILE_PATH,
        help='Path to configuration file'
    )
    args = parser.parse_args()
    config_path = args.config
    print("config_path:", config_path)
    return config_path


def parse_config(def_config, config_path):
    parser = configparser.ConfigParser()
    parser.read(config_path)
    config = def_config.copy()

    if not os.path.isfile(config_path):
        raise Exception("Config file not found")
    try:
        for key in parser["log_analyzer"].keys():
            config[key.upper()] = parser["log_analyzer"][key]
        return config
    except configparser.Error:
        raise


def search_last_logfile(log_dir):
    # list of files in log_dir
    file_names = os.listdir(log_dir)
    # list of files with path
    files = [os.path.join(log_dir, file_name) for file_name in file_names]
    return

def parse_logfile():
    file = None
    file_data = None
    yield (file, file_date)


def create_report():
    pass


def create_report_template():
    pass


def main():
    print('hello')
    config_path = get_config_path()
    config = parse_config(default_config, config_path)
    print(config)


if __name__ == "__main__":
    main()
