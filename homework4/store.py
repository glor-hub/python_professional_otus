# -*- coding: utf-8 -*-
import logging

import redis

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_TIMEOUT = 2


class RedisStorage:
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, timeout=REDIS_TIMEOUT):
        self.host = host
        self.port = port
        self.db=None
        self.timeout = timeout

    def connect(self):
        self.db = redis.StrictRedis(
            host=self.host,
            port=self.port,
            db=0,
            socket_timeout=self.timeout,
            socket_connect_timeout=self.timeout,
            encoding="utf-8",
            decode_responses=True
        )

    def set(self, key, value, expire):
        try:
            return self.db.set(key, value, ex=expire)
        except redis.DataError:
            logging.exception('Invalid input of type')
            raise
        except redis.TimeoutError:
            logging.exception('Timeout error occurred')
            raise TimeoutError
        except redis.RedisError:
            raise ConnectionError

    def get(self, key):
        try:
            return self.db.get(key)
        except (AttributeError, ValueError):
            return None
        except redis.TimeoutError:
            logging.exception('Timeout error occurred')
            raise TimeoutError
        except redis.RedisError:
            raise ConnectionError


class Store:
    def __init__(self, storage, max_retries):
        self.storage = storage
        self.max_retries = max_retries

    def connect(self):
        self.storage.connect()

    def get(self, key):
        return self.storage.get(key)

    def cache_get(self, key):
        num_retries = 0
        while num_retries < self.max_retries:
            try:
                return self.storage.get(key)
            except ConnectionError:
                self.storage.connect()
                num_retries += 1
                if num_retries > self.max_retries:
                    raise ConnectionError

    def cache_set(self, key, value, expire=0):
        num_retries = 0
        while num_retries < self.max_retries:
            try:
                return self.storage.set(key, value, expire)
            except ConnectionError:
                self.storage.connect()
                num_retries += 1
                if num_retries > self.max_retries:
                    raise ConnectionError
