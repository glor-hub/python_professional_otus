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
    "ERROR_THRESHOLD_PERCENT": 12
}

DEFAULT_CONFIG_FILE_PATH = os.path.abspath('config.ini')
LOG_FILE_REGEX = re.compile(r'nginx-access-ui\.log-(\d{8})(\.(gz|plain|txt)?)$')
LOG_FILE_DATETIME_FORMAT = '%Y%m%d'
REPORT_FILE_DATETIME_FORMAT = '%Y.%m.%d'
LastLogFile = namedtuple('LastLogFile', ['path', 'ext', 'date'])
LastLogRow = namedtuple('LastLogRow', ['url', 'response_time'])


def get_config_path():
    # parse the command line to get config path
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config',
        default=DEFAULT_CONFIG_FILE_PATH,
        help='Path to configuration file'
    )
    args = parser.parse_args()
    config_path = args.config
    return config_path


def parse_config(def_config, config_path):
    # update config from config file
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
    # parse objects in log directory and find last created file
    last_log_date = 0
    last_log_file = None
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
        return
    else:
        last_log_file_path = os.path.join(log_dir, last_log_file)
        last_log_file_ext = os.path.splitext(last_log_file_path)[1]
    return LastLogFile(
        path=last_log_file_path,
        ext=last_log_file_ext,
        date=last_log_date
    )


def gen_parse_logfile(log_file):
    # function-generator parse log file content and yeild url and response time from log rows
    opener = gzip.open if log_file.ext == '.gz' else open
    with opener(log_file.path, 'rt', encoding='utf-8') as file:
        for row in file:
            try:
                row_parts = row.strip().split()
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
        return


def calculate_data(log_rows, err_threshold_perc, rows_sum):
    # data processing for create report
    all_count_sum = 0
    fault_count_sum = 0
    all_time_sum = 0
    data = {}
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
        data[url]['url'] = url
        data[url]['time_sum'] = round(data[url]['time_sum'], 3)
        data[url]['count_perc'] = round((data[url]['count'] / all_count_sum) * 100.0, 3)
        data[url]['time_perc'] = round((data[url]['time_sum'] / all_time_sum) * 100.0, 3)
        data[url]['time_avg'] = round(data[url]['time_sum'] / data[url]['count'], 3)
        data[url]['time_max'] = round(max(data[url]['time_list']), 3)
        data[url]['time_med'] = round(median(data[url]['time_list']), 3)
        del data[url]['time_list']

    logging.info('%d rows calculated' % len(data))
    sorted_data = (sorted(data.values(), key=lambda x: x['time_sum'], reverse=True))[:int(rows_sum)]
    error_parse_perc = (fault_count_sum / all_count_sum) * 100.0
    # error_parse_perc = 85
    if err_threshold_perc < 0:
        logging.error("err_threshold_perc %2.2f must be positive."
                      % (err_threshold_perc, error_parse_perc))
        raise Exception
    if error_parse_perc > float(err_threshold_perc):
        logging.error("Error percentage threshold %2.2f exceeded. Current error percentage: %2.2f."
                      % (err_threshold_perc, error_parse_perc))
        raise Exception
    return sorted_data


def get_report_path(log_file, report_dir):
    # generate file name and path for html-report
    try:
        log_datetime = datetime.strptime(str(log_file.date), LOG_FILE_DATETIME_FORMAT)
    except Exception:
        logging.error('Can`t parse string %s to datetime object', str(log_file.date))
        raise
    file_name = 'report-%s.html' % log_datetime.strftime(REPORT_FILE_DATETIME_FORMAT)
    file_path = os.path.join(report_dir, file_name)
    return file_path


def create_report(report_path, template_path, data):
    # render template with use template and obtained data
    try:
        with open(template_path, 'rt', encoding='utf-8') as src:
            template = Template(src.read())
            new_template = template.safe_substitute(table_json=json.dumps(data))
        with open(report_path, 'w', encoding='utf-8') as dst:
            dst.write(new_template)
    except Exception:
        logging.error('Error occurred while creating %s', repr(report_path))
        raise


def logging_init(logging_file):
    # initialize script logging
    logging.basicConfig(filename=logging_file,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)


def main():
    config_path = get_config_path()
    config = parse_config(default_config, config_path)
    try:
        logging_init(config['LOGGING_FILE'])
    except Exception:
        logging_init(None)
    logging.info('Config = %s' % config)
    logging.info('Start search latest Logfile in dir %s' % repr(config['LOG_DIR']))
    log_file = (search_last_logfile(config['LOG_DIR'], LOG_FILE_REGEX))
    if not log_file:
        logging.info('Logfile not found')
        return
    if not os.path.getsize(log_file.path):
        logging.info('Logfile is empty')
        return
    logging.info('Latest Logfile: %s' % repr(log_file.path))
    log_parser_generator = gen_parse_logfile(log_file)
    try:
        report_file = get_report_path(log_file, config['REPORT_DIR'])
    except Exception:
        logging.error('Report directory not found')
        raise
    template_file = os.path.join(config['REPORT_DIR'], 'report.html')
    if not os.path.isfile(template_file):
        logging.error('Template file %s not found' % repr(template_file))
        raise Exception
    if os.path.exists(report_file):
        logging.info('Report %s already exist.' % repr(report_file))
        return
    logging.info('Start calculating')
    data = calculate_data(log_parser_generator, config['ERROR_THRESHOLD_PERCENT'], config['REPORT_SIZE'])
    logging.info('%d rows calculated' % len(data))
    logging.info('Start creating report')
    create_report(report_file, template_file, data)
    logging.info('New report %s created' % repr(report_file))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.exception("Unexpected error occurred")
        raise
