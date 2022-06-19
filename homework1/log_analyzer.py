#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import gzip
import logging
import os
import argparse
import configparser
import re
from collections import namedtuple

default_config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "LOGGING_FILE": "log_analyzer.log"
}

DEFAULT_CONFIG_FILE_PATH = os.path.abspath('config.ini')
LOG_FILE_REGEX = re.compile(r'nginx-access-ui\.log-(\d{8})(\.(gz|plain|txt)?)$')
LastLogFile = namedtuple('LastLogFile', ['path', 'ext', 'date'])
LastLogRow = namedtuple('LastLogRow', ['url', 'response_time'])


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


def search_last_logfile(log_dir, logfile_regex):
    last_log_date = 0
    last_log_file = None
    last_log_file_ext = None
    last_log_file_path = None
    # list of files in log_dir
    files = os.listdir(log_dir)
    for file in files:
        if not os.path.isfile(os.path.join(log_dir, file)):
            continue
        match = re.search(logfile_regex, file)
        if not match:
            continue
        file_date = int(match.group(1))
        if file_date > last_log_date:
            last_log_date = file_date
            last_log_file = file
    if not last_log_file:
        logging.info = 'Logfile not found'
    else:
        last_log_file_path = os.path.join(log_dir, last_log_file)
        last_log_file_ext = os.path.splitext(last_log_file_path)[1]
    return LastLogFile(
        path=last_log_file_path,
        ext=last_log_file_ext,
        date=last_log_date
    )


def gen_parse_logfile(log_file):
    opener = gzip.open if log_file.ext == '.gz' else open
    success_parse_count = 0
    fault_parse_count = 0
    with opener(log_file.path, 'rt', encoding='utf-8') as file:
        for row in file:
            try:
                row_parts = row.split()
                url = row_parts[6]
                response_time = float(row_parts[-1])
            except Exception:
                url = None
                response_time = None
                logging.error('Can`t parse row %s', row)
            finally:
                yield LastLogRow(
                    url=url,
                    response_time=response_time
                )


def create_report(log_rows):
    success_parse_count = 0
    fault_parse_count = 0
    sum_time = 0
    data = {}

    for url, time in log_rows:
        if url == None or time == None:
            fault_parse_count += 1
        else:
            sum_time += time
            data[url] = data.get(url, {'time': 0, 'count': 0})
            data[url]['time'] += time
            data[url]['count'] += 1
            success_parse_count += 1
    sum_count = success_parse_count + fault_parse_count
    print(data)


def create_report_template():
    pass


def logging_init():
    logging.basicConfig(filename="LOGGING_FILE",
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)


def main():
    print('hello')
    logging_init()
    config_path = get_config_path()
    config = parse_config(default_config, config_path)
    print(config)
    log_file = (search_last_logfile(config['LOG_DIR'], LOG_FILE_REGEX))
    log_parser_generator = gen_parse_logfile(log_file)
    create_report(log_parser_generator)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.exception("Unexpected error occurred")
        raise
