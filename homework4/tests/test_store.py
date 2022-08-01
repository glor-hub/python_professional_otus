import unittest
from unittest.mock import patch
import fakeredis

import store

class TestStoreOnConnectSuccess(unittest.TestCase):
    @patch("redis.StrictRedis", fakeredis.FakeStrictRedis)
    def setUp(self):
        self.redis_storage = store.RedisStorage()
        self.redis_storage.connect()
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

class TestStoreOnConnectError(unittest.TestCase):
    def setUp(self):
        server = fakeredis.FakeServer()
        server.connected = False
        self.redis_storage = store.RedisStorage()
        self.redis_storage.db=fakeredis.FakeStrictRedis(server=server)
        self.store = store.Store(self.redis_storage,1)

    def tearDown(self):
        self.redis_storage.db.close()

    def test_raises_set_and_get_data_to_db(self):
        with self.assertRaises(ConnectionError):
            self.redis_storage.set("key1","value1",600)
        with self.assertRaises(ConnectionError):
            self.redis_storage.get("key1")

    def test_failed_set_and_get_cache_data_to_store(self):

        self.assertEqual(self.store.cache_set("foo3", "bar3",600), None)
        self.assertEqual(self.store.cache_get("foo3"), None)
        self.assertEqual(self.store.get("foo3"), None)

if __name__ == "__main__":
    unittest.main()
    