import os
import unittest
import log_analyzer

TEST_FIXTURE_DIR = "tests/fixture"


class GetParseConfigTestCase(unittest.TestCase):
    def setUp(self):
        self.test_config = {
            "TEST_REPORT_SIZE": 5,
            "TEST_REPORT_DIR": "tests/report",
            "TEST_LOG_DIR": "tests/log",
            "TEST_ERROR_THRESHOLD_PERCENT": 18.0
        }
        self.TEST_INVALID_CONFIG_FILE_PATH = ''
        self.TEST_EMPTY_CONFIG_FILE = 'invalid_config.ini'
        self.TEST_VALID_CONFIG_FILE = 'valid_config.ini'
        self.TEST_CONFIG_DIR = "tests/config"
        os.mkdir(self.TEST_CONFIG_DIR)

    def tearDown(self):
        for filename in os.listdir(self.TEST_CONFIG_DIR):
            os.remove(os.path.join(self.TEST_CONFIG_DIR, filename))
        os.rmdir(self.TEST_CONFIG_DIR)

    def test_default_config_path(self):
        config_path = log_analyzer.get_config_path()
        self.assertEqual(config_path, log_analyzer.DEFAULT_CONFIG_FILE_PATH)

    def test_failed_parse_config_with_invalid_path(self):
        with self.assertRaises(Exception):
            log_analyzer.parse_config(self.test_config, self.TEST_INVALID_CONFIG_FILE_PATH)

    #
    def test_failed_parse_config_with_invalid_content_file(self):
        f = open(os.path.join(self.TEST_CONFIG_DIR, self.TEST_EMPTY_CONFIG_FILE), "x")
        f.close()
        with self.assertRaises(Exception):
            log_analyzer.parse_config(self.test_config,
                                      os.path.join(self.TEST_CONFIG_DIR, self.TEST_EMPTY_CONFIG_FILE))

    def test_parse_config_with_valid_content_file(self):
        with open(os.path.join(self.TEST_CONFIG_DIR, self.TEST_VALID_CONFIG_FILE), "w") as f:
            f.write('[log_analyzer]\n')
            f.write('TEST_REPORT_SIZE = 25')
        config = log_analyzer.parse_config(self.test_config,
                                           os.path.join(self.TEST_CONFIG_DIR, self.TEST_VALID_CONFIG_FILE))
        self.assertEqual(config['TEST_REPORT_SIZE'], '25')


class SearchLastLogFileTestCase(unittest.TestCase):
    def setUp(self):
        self.test_config = {
            "TEST_REPORT_SIZE": 5,
            "TEST_REPORT_DIR": "tests/report",
            "TEST_LOG_DIR": "tests/log",
            "TEST_ERROR_THRESHOLD_PERCENT": 18.0
        }
        self.TEST_INVALID_LOG_FILE_NAME = '123.gz'
        self.TEST_INVALID_LOG_FILE_EXT = 'nginx-access-ui.log-20150921.bz2'
        self.TEST_EMPTY_LOG_FILE = 'nginx-access-ui.log-20160123.gz'
        os.mkdir(self.test_config['TEST_LOG_DIR'])

    def tearDown(self):
        for filename in os.listdir(self.test_config['TEST_LOG_DIR']):
            os.remove(os.path.join(self.test_config['TEST_LOG_DIR'], filename))
        os.rmdir(self.test_config['TEST_LOG_DIR'])

    def test_log_file_invalid_ext(self):
        f = open(os.path.join(self.test_config['TEST_LOG_DIR'], self.TEST_INVALID_LOG_FILE_EXT), "x")
        f.close()
        last_log_file = log_analyzer.search_last_logfile(self.test_config['TEST_LOG_DIR'], log_analyzer.LOG_FILE_REGEX)
        self.assertEqual(last_log_file, None)

    def test_log_file_invalid_name(self):
        f = open(os.path.join(self.test_config['TEST_LOG_DIR'], self.TEST_INVALID_LOG_FILE_NAME), "x")
        f.close()
        last_log_file = log_analyzer.search_last_logfile(self.test_config['TEST_LOG_DIR'], log_analyzer.LOG_FILE_REGEX)
        self.assertEqual(last_log_file, None)

    def test_non_empty_log_file(self):
        with open(os.path.join(self.test_config['TEST_LOG_DIR'], self.TEST_EMPTY_LOG_FILE), "w") as f:
            f.write('Test string')
        last_log_file = log_analyzer.search_last_logfile(self.test_config['TEST_LOG_DIR'], log_analyzer.LOG_FILE_REGEX)
        self.assertIsNotNone(last_log_file)

    def test_get_latest_logfile(self):
        filenames = (
            'nginx-access-ui.log-20220101.gz',
            'nginx-access-ui.log-20220102.gz',
            'nginx-access-ui.log-20220103.gz'
        )
        for file in filenames:
            f = open(os.path.join(self.test_config['TEST_LOG_DIR'], file), "x")
            f.close()
        last_log_file = log_analyzer.search_last_logfile(self.test_config['TEST_LOG_DIR'], log_analyzer.LOG_FILE_REGEX)
        self.assertEqual(
            last_log_file.date, 20220103
        )


class GenParseLogFileTestCase(unittest.TestCase):
    def setUp(self):
        self.test_config = {
            "TEST_REPORT_SIZE": 5,
            "TEST_REPORT_DIR": "tests/report",
            "TEST_LOG_DIR": "tests/log",
            "TEST_ERROR_THRESHOLD_PERCENT": 18.0
        }
        self.TEST_SAMPLE_LOG_FILE = 'nginx-access-ui.log-20170629.txt'

    def test_parse_log_file(self):
        log_file = log_analyzer.search_last_logfile(TEST_FIXTURE_DIR, log_analyzer.LOG_FILE_REGEX)
        rows = log_analyzer.gen_parse_logfile(log_file)
        logrow = []
        for url, time in rows:
            logrow.append(log_analyzer.LastLogRow(url=url, response_time=time))
        self.assertEqual(logrow[0].url, '/api/v2/banner/25019354')
        self.assertEqual(logrow[0].response_time, 0.390)
        self.assertEqual(logrow[1].url, '/api/1/photogenic_banners/list/?server_name=WIN7RB4')
        self.assertEqual(logrow[1].response_time, 0.133)
        self.assertEqual(logrow[2].url, '/api/v2/banner/16852664')
        self.assertEqual(logrow[2].response_time, 0.199)


class CalculateDataTestCase(unittest.TestCase):
    def setUp(self):
        self.test_config = {
            "TEST_REPORT_SIZE": 5,
            "TEST_REPORT_DIR": "tests/report",
            "TEST_LOG_DIR": "tests/log",
            "TEST_ERROR_THRESHOLD_PERCENT": 18.0
        }
        self.TEST_SAMPLE_LOG_FILE = 'nginx-access-ui.log-20170629.txt'

    def test_processing_data(self):
        log_file = log_analyzer.search_last_logfile(TEST_FIXTURE_DIR, log_analyzer.LOG_FILE_REGEX)
        rows = log_analyzer.gen_parse_logfile(log_file)
        data = log_analyzer.calculate_data(rows, self.test_config["TEST_ERROR_THRESHOLD_PERCENT"],
                                           self.test_config['TEST_REPORT_SIZE'])
        time_sum = round(0.390 + 0.704, 3)
        count_perc = round(2 * 100 / 5, 3)
        time_perc = round((0.390 + 0.704) / (0.390 + 0.133 + 0.199 + 0.704 + 0.146) * 100, 3)
        time_avg = round((0.390 + 0.704) / 2, 3)
        time_max = 0.704
        time_med = 0.547
        self.assertEqual(data[0]['url'], '/api/v2/banner/25019354')
        self.assertEqual(data[0]['time_sum'], time_sum)
        self.assertEqual(data[0]['count_perc'], count_perc)
        self.assertEqual(data[0]['time_perc'], time_perc)
        self.assertEqual(data[0]['time_avg'], time_avg)
        self.assertEqual(data[0]['time_max'], time_max)
        self.assertEqual(data[0]['time_med'], time_med)

    def test_fail_error_threshold_percentage(self):
        err_threshold = -8
        log_file = log_analyzer.search_last_logfile(TEST_FIXTURE_DIR, log_analyzer.LOG_FILE_REGEX)
        rows = log_analyzer.gen_parse_logfile(log_file)
        with self.assertRaises(Exception):
            log_analyzer.calculate_data(rows, err_threshold, self.test_config['TEST_REPORT_SIZE'])

    def test_processing_data_is_sorted(self):
        rows = [log_analyzer.LastLogRow(url=i, response_time=i) for i in range(1, 10)]
        data = log_analyzer.calculate_data(rows, self.test_config["TEST_ERROR_THRESHOLD_PERCENT"], 9)
        self.assertEqual(data[0]['time_sum'], 9)
        self.assertEqual(data[-1]['time_sum'], 1)


class CreateReportTestCase(unittest.TestCase):
    def setUp(self):
        self.test_config = {
            "TEST_REPORT_SIZE": 5,
            "TEST_REPORT_DIR": "tests/report",
            "TEST_LOG_DIR": "tests/log",
            "TEST_ERROR_THRESHOLD_PERCENT": 18.0
        }
        self.TEST_REPORT_TEMPLATE = 'template.html'
        os.mkdir(self.test_config["TEST_REPORT_DIR"])

    def tearDown(self):
        for filename in os.listdir(self.test_config["TEST_REPORT_DIR"]):
            os.remove(os.path.join(self.test_config["TEST_REPORT_DIR"], filename))
        os.rmdir(self.test_config["TEST_REPORT_DIR"])

    def test_create_report(self):
        template_file = os.path.join(TEST_FIXTURE_DIR, self.TEST_REPORT_TEMPLATE)
        report_file = os.path.join(self.test_config['TEST_REPORT_DIR'], 'test_report.html')
        time_sum = 50
        count_perc = round(2 * 100 / 5, 3)
        time_perc = 20
        time_avg = 15
        time_max = 35
        time_med = 30
        data = [{'url': '/api/v2/banner/25019354',
            'time_sum': time_sum,
            'count_perc': count_perc,
            'time_perc': time_perc,
            'time_avg': time_avg,
            'time_max': time_max,
            'time_med': time_med
        }]
        log_analyzer.create_report(report_file, template_file, data)
        self.assertEqual(os.path.exists(report_file), True)

if __name__ == '__main__':
    unittest.main()
