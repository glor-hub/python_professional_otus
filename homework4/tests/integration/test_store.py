import unittest
import time
from unittest.mock import Mock
from app.store import RedisStorage, Store

class TestStoreOnConnectSuccess(unittest.TestCase):
    def setUp(self):
        self.redis_storage = RedisStorage()
        self.redis_storage.connect()
        self.store = Store(self.redis_storage,10,3)

    def tearDown(self):
        self.redis_storage.db.close()

    def test_db_data_set_get(self):
        self.assertEqual(self.redis_storage.set("key","value",600), True)
        self.assertEqual(self.redis_storage.get("key"), "value")
        self.assertEqual(self.redis_storage.get("ke"), None)

    def test_store_cache(self):
        self.assertEqual(self.store.cache_set("foo", "bar",600), True)
        self.assertEqual(self.store.cache_get("foo"), "bar")
        self.assertEqual(self.store.get("foo"), "bar")

    def test_store_cache_expire(self):
        self.assertEqual(self.store.cache_set("foo1", "bar1",1), True)
        time.sleep(1)
        self.assertIsNone(self.store.cache_get("foo1"))

    def test_store_get(self):
        self.assertEqual(self.store.cache_set("baz", "100",600), True)
        self.assertEqual(self.store.get("baz"), "100")

class TestStoreOnConnectError(unittest.TestCase):
    def setUp(self):
        self.redis_storage = RedisStorage()
        self.redis_storage.connect()
        self.store = Store(self.redis_storage,2,2)
        self.redis_storage.set = Mock(side_effect=ConnectionError)
        self.redis_storage.get = Mock(side_effect=ConnectionError)

    def tearDown(self):
        self.redis_storage.db.close()

    def test_raises_db_data_set_get(self):
        with self.assertRaises(ConnectionError):
            self.redis_storage.set("key1","value1",20)
        with self.assertRaises(ConnectionError):
            self.redis_storage.get("key1")

    def test_error_store_cache(self):
        self.assertIsNone(self.store.cache_set("key2", "value2",20))
        self.assertIsNone(self.store.cache_get("key2"))

    def test_raises_store_get(self):
        with self.assertRaises(ConnectionError):
            self.store.get("key2")

if __name__ == "__main__":
    unittest.main()
