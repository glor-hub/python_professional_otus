import os
import unittest
import homework1.log_analyzer
from homework1 import log_analyzer


class GetParseConfigTestCase(unittest.TestCase):
    def setUp(self):
        self.test_config = {
            "TEST_REPORT_SIZE": 5,
            "TEST_REPORT_DIR": "./report",
            "TEST_LOG_DIR": "./log",
            "TEST_ERROR_THRESHOLD_PERCENT": 18.0
        }
        self.TEST_INVALID_CONFIG_FILE_PATH = ''
        self.TEST_EMPTY_CONFIG_FILE = 'invalid_config.ini'
        self.TEST_VALID_CONFIG_FILE = 'valid_config.ini'
        self.TEST_CONFIG_DIR = "./config"
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
            "TEST_REPORT_DIR": "./report",
            "TEST_LOG_DIR": "./log",
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

    def test_log_file_is_empty(self):
        f = open(os.path.join(self.test_config['TEST_LOG_DIR'], self.TEST_EMPTY_LOG_FILE), "x")
        f.close()
        last_log_file = log_analyzer.search_last_logfile(self.test_config['TEST_LOG_DIR'], log_analyzer.LOG_FILE_REGEX)
        logfile_is_empty=log_analyzer.logfile_is_empty(last_log_file)
        self.assertEqual(logfile_is_empty, True)

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
            "TEST_REPORT_DIR": "./report",
            "TEST_LOG_DIR": "./log",
            "TEST_ERROR_THRESHOLD_PERCENT": 18.0
        }
        self.TEST_SAMPLE_LOG_FILE = 'nginx-access-ui.log-20160123.txt'
        os.mkdir(self.test_config['TEST_LOG_DIR'])

    def tearDown(self):
        def tearDown(self):
            for filename in os.listdir(self.test_config['TEST_LOG_DIR']):
                os.remove(os.path.join(self.test_config['TEST_LOG_DIR'], filename))
            os.rmdir(self.test_config['TEST_LOG_DIR'])


if __name__ == '__main__':
    unittest.main()
