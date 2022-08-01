import unittest
from unittest.mock import patch, MagicMock
import fakeredis

import store

class TestStoreOnConnectSuccess(unittest.TestCase):
    @patch("redis.StrictRedis", fakeredis.FakeStrictRedis)
    def setUp(self):
        self.redis_storage = store.RedisStorage()
        self.redis_storage.connect()
        self.redis_storage.db.connected = True
        self.store = store.Store(self.redis_storage,3)

    @patch("redis.StrictRedis", fakeredis.FakeStrictRedis)
    def tearDown(self):
        self.redis_storage.db.close()

    @patch("redis.StrictRedis", fakeredis.FakeStrictRedis)
    def test_set_and_get_data_to_db(self):
        self.assertEqual(self.redis_storage.set("key","value",600), True)
        self.assertEqual(self.redis_storage.get("key"), "value")
        self.assertEqual(self.redis_storage.get("ke"), None)

    @patch("redis.StrictRedis", fakeredis.FakeStrictRedis)
    def test_set_and_get_cache_data_to_store(self):
        self.assertEqual(self.store.cache_set("foo", "bar",600), True)
        self.assertEqual(self.store.cache_get("foo"), "bar")
        self.assertEqual(self.store.get("foo"), "bar")



if __name__ == "__main__":
    unittest.main()