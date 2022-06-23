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

    def test_parse_config_with_incorrect_path(self):
        with self.assertRaises(Exception):
            log_analyzer.parse_config(self.test_config, os.path.abspath('./tests/incorrect_config.ini'))

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

    def test_log_file_extention(self):
        # os.mkdir(self.test_config['TEST_LOG_DIR'])
        # with open(os.path.join(self.test_config['TEST_LOG_DIR'], '123.txt'), "w"):
        #     pass
        last_log_file = log_analyzer.search_last_logfile(self.test_config['TEST_LOG_DIR']
                                                       ,log_analyzer.LOG_FILE_REGEX)
        print(last_log_file)
        # self.assertEqual(config_path, log_analyzer.DEFAULT_CONFIG_FILE_PATH)


if __name__ == '__main__':
    unittest.main()
