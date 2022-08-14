import unittest
from unittest.mock import patch, Mock
import fakeredis

from app.appstore import RedisStorage, Store


class TestStoreOnConnectSuccess(unittest.TestCase):
    @patch("redis.StrictRedis", fakeredis.FakeStrictRedis)
    def setUp(self):
        self.redis_storage = RedisStorage()
        self.redis_storage.connect()
        self.store = Store(self.redis_storage,10,3)

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
        self.redis_storage = RedisStorage()
        self.redis_storage.db=fakeredis.FakeStrictRedis(server=server)
        self.store = Store(self.redis_storage,3,0)

    def tearDown(self):
        self.redis_storage.db.close()

    def with_raise_connection(self):
        self.redis_storage.connect= Mock(side_effect=ConnectionError)

    def with_raise_connection(self):
        self.redis_storage.connect = Mock(side_effect=ConnectionError)

    def test_raises_set_and_get_data_to_db(self):
        with self.assertRaises(ConnectionError):
            self.redis_storage.set("key1","value1",20)
        with self.assertRaises(ConnectionError):
            self.redis_storage.get("key1")

    def test_raises_set_and_get_cache_data_to_store(self):
        self.with_raise_connection()
        with self.assertRaises(ConnectionError):
            self.store.cache_set("foo1", "bar1",20)
        with self.assertRaises(ConnectionError):
            self.store.cache_get("foo1")

    def test_failed_get_cache_data_to_store(self):
        self.assertIsNone(self.store.cache_get("foo3"))
        self.assertIsNone(self.store.get("foo3"))

if __name__ == "__main__":
    unittest.main()
