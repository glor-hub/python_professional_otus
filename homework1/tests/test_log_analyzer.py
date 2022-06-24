import os
import unittest
import log_analyzer


class GetParseConfigTestCase(unittest.TestCase):
    def setUp(self):
        self.test_config = {
            "TEST_REPORT_SIZE": 5,
            "TEST_REPORT_DIR": "./tests/report",
            "TEST_LOG_DIR": "./tests/log",
            "TEST_ERROR_THRESHOLD_PERCENT": 18.0
        }
        self.INVALID_CONFIG_FILE_PATH = ''

    def test_default_config_path(self):
        config_path = log_analyzer.get_config_path()
        self.assertEqual(config_path, log_analyzer.DEFAULT_CONFIG_FILE_PATH)

    def test_parse_config_with_invalid_path(self):
        with self.assertRaises(Exception):
            log_analyzer.parse_config(self.test_config, self.INVALID_CONFIG_FILE_PATH)

    def test_parse_config_with_invalid_path(self):
        with self.assertRaises(Exception):
            log_analyzer.parse_config(self.test_config, os.path.abspath('./tests/invalid_config.ini'))

    def test_update_config_from_file(self):
        config = log_analyzer.parse_config(self.test_config, os.path.abspath('./tests/test_config.ini'))
        self.assertEqual(config['TEST_REPORT_SIZE'], '25')


class SearchLastLogfileTestCase(unittest.TestCase):
    def setUp(self):
        self.test_config = {
            "TEST_REPORT_SIZE": 5,
            "TEST_REPORT_DIR": "./tests/report",
            "TEST_LOG_DIR": "./tests/log",
            "TEST_ERROR_THRESHOLD_PERCENT": 18.0
        }
        self.TEST_INVALID_LOG_FILE_NAME = '123.gz'
        self.TEST_INVALID_LOG_FILE_EXT = 'nginx-access-ui.log-20150921.bz2'
        self.TEST_EMPTY_LOG_FILE = 'nginx-access-ui.log-20160123.gz'
        os.mkdir(self.test_config['TEST_LOG_DIR'])

    def tearDown(self):
        os.rmdir(self.test_config['TEST_LOG_DIR'])

    def test_log_file_is_empty(self):
        f = open(os.path.join(self.test_config['TEST_LOG_DIR'], self.TEST_EMPTY_LOG_FILE), "x")
        f.close()
        last_log_file = log_analyzer.search_last_logfile(self.test_config['TEST_LOG_DIR']
                                                         , log_analyzer.LOG_FILE_REGEX)
        self.assertEqual(last_log_file, None)

    def test_log_file_invalid_ext(self):
        f = open(os.path.join(self.test_config['TEST_LOG_DIR'], self.TEST_INVALID_LOG_FILE_EXT), "x")
        f.close()
        last_log_file = log_analyzer.search_last_logfile(self.test_config['TEST_LOG_DIR']
                                                         , log_analyzer.LOG_FILE_REGEX)
        self.assertEqual(last_log_file, None)

    def test_log_file_invalid_name(self):
        f = open(os.path.join(self.test_config['TEST_LOG_DIR'], self.TEST_INVALID_LOG_FILE_NAME), "x")
        f.close()
        last_log_file = log_analyzer.search_last_logfile(self.test_config['TEST_LOG_DIR']
                                                         , log_analyzer.LOG_FILE_REGEX)
        self.assertEqual(last_log_file, None)

    def test_non_empty_log_file(self):
        with open(os.path.join(self.test_config['TEST_LOG_DIR'], self.TEST_EMPTY_LOG_FILE), "w") as f:
            f.write('Test string')
        last_log_file = log_analyzer.search_last_logfile(self.test_config['TEST_LOG_DIR']
                                                         , log_analyzer.LOG_FILE_REGEX)
        self.assertIsNotNone(last_log_file)


if __name__ == '__main__':
    unittest.main()
