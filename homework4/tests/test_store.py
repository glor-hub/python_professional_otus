import unittest
from unittest.mock import patch, MagicMock
import fakeredis

import store

class TestStoreOnConnectSuccess(unittest.TestCase):
    def setUp(self):
        self.redis_storage = store.RedisStorage()
        self.redis_storage.connect()
        self.redis_storage.db.connected = True
        self.store = store.Store(self.redis_storage,3)

    def tearDown(self):
        self.redis_storage.db.close()

    @patch("redis.StrictRedis", fakeredis.FakeStrictRedis)
    def test_set_valid_data_to_db(self):
        self.assertEqual(self.redis_storage.set("key","value",600), True)

    @patch("redis.StrictRedis", fakeredis.FakeStrictRedis)
    def test_get_valid_data_from_db(self):
        self.assertEqual(self.redis_storage.get("key"), "value")

    @patch("redis.StrictRedis", fakeredis.FakeStrictRedis)
    def test_get_non_exist_data_from_db(self):
        self.assertNotEqual(self.redis_storage.get("ke"), "value")
        self.assertEqual(self.redis_storage.get("ke"), None)


    @patch("redis.StrictRedis", fakeredis.FakeStrictRedis)
    def test_get_valid_data_from_store(self):
        self.assertEqual(self.store.get("key"), "value")

    @patch("redis.StrictRedis", fakeredis.FakeStrictRedis)
    def test_set_cache_data_to_store(self):
        self.assertEqual(self.store.cache_set("foo", "bar",600), True)

    @patch("redis.StrictRedis", fakeredis.FakeStrictRedis)
    def test_get_cache_data_from_store(self):
        self.assertEqual(self.store.cache_get("foo"), "bar")


if __name__ == "__main__":
    unittest.main()