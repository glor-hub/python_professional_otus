import os
import unittest
import log_analyzer


class GetConfigPathTestCase(unittest.TestCase):
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

    def test_parse_config_with_uncorrect_path(self):
        with self.assertRaises(Exception):
            log_analyzer.parse_config(self.test_config, os.path.abspath('test/uncorrect_config.ini'))

if __name__ == '__main__':
    unittest.main()
