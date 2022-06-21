#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import gzip
import json
import logging
import os
import argparse
import configparser
import re
from collections import namedtuple
from datetime import datetime
from statistics import median
from string import Template

default_config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "LOGGING_FILE": "log_analyzer.log",
    "ERROR_THRESHOLD_PERCENT": 10.0
}

DEFAULT_CONFIG_FILE_PATH = os.path.abspath('config.ini')
LOG_FILE_REGEX = re.compile(r'nginx-access-ui\.log-(\d{8})(\.(gz|plain|txt)?)$')
LOG_FILE_DATETIME_FORMAT = '%Y%m%d'
REPORT_FILE_DATETIME_FORMAT = '%Y.%m.%d'
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


def calculate_data(log_rows, err_threshold_perc, rows_sum):
    all_count_sum = 0
    fault_count_sum = 0
    all_time_sum = 0
    data = {}
    rows_count = 0
    for url, time in log_rows:
        all_count_sum += 1
        if url == None or time == None:
            fault_count_sum += 1
        else:
            all_time_sum += time
            data[url] = data.get(url, {'count': 0, 'time_sum': 0, 'time_list': []})
            data[url]['count'] += 1
            data[url]['time_sum'] += time
            data[url]['time_list'].append(time)

    for url in data.keys():
        if (rows_count <= int(rows_sum)):
            data[url]['url'] = url
            data[url]['time_sum'] = round(data[url]['time_sum'], 3)
            data[url]['count_perc'] = round((data[url]['count'] / all_count_sum) * 100.0, 3)
            data[url]['time_perc'] = round((data[url]['time_sum'] / all_time_sum) * 100.0, 3)
            data[url]['time_avg'] = round(data[url]['time_sum'] / data[url]['count'], 3)
            data[url]['time_max'] = round(max(data[url]['time_list']), 3)
            data[url]['time_med'] = round(median(data[url]['time_list']), 3)
            del data[url]['time_list']

    sorted_data = sorted(data.values(), key=lambda x: x['time_sum'], reverse=True)
    error_parse_perc = (fault_count_sum / all_count_sum) * 100.0
    if error_parse_perc > float(err_threshold_perc):
        logging.error("Error")
        raise Exception
    print(sorted_data[0])
    return sorted_data


def get_report_path(log_file, report_dir):
    log_datetime = datetime.strptime(str(log_file.date), LOG_FILE_DATETIME_FORMAT)
    file_name = 'report-%s.html' % log_datetime.strftime(REPORT_FILE_DATETIME_FORMAT)
    file_path = os.path.join(report_dir, file_name)
    return file_path


def get_template_path(report_dir):
    template_path = os.path.join(report_dir, 'report.html')
    return template_path


def create_report(report_path, template_path, data):
    with open(template_path, 'rt', encoding='utf-8') as src:
        template = Template(src.read())
        new_template = template.safe_substitute(table_json=json.dumps(data))

    with open(report_path, 'w', encoding='utf-8') as dst:
        dst.write(new_template)


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
    data = calculate_data(log_parser_generator, config['ERROR_THRESHOLD_PERCENT'], config['REPORT_SIZE'])
    report_file = get_report_path(log_file, config['REPORT_DIR'])
    template_file = get_template_path(config['REPORT_DIR'])
    create_report(report_file, template_file, data)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.exception("Unexpected error occurred")
        raise
