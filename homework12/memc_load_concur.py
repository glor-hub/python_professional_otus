#!/usr/bin/env python
# -*- coding: utf-8 -*-
from functools import partial
import os
import gzip
import sys
import time
import glob
import logging
import collections
from optparse import OptionParser
# brew install protobuf
# protoc  --python_out=. ./appsinstalled.proto
# pip install protobuf
import appsinstalled_pb2
# pip install python-memcached
import memcache
from multiprocessing import Pool
import queue
import threading

WORKERS_COUNT = os.cpu_count()
THREADS_IN_WORKER_COUNT = 5

MEMC_SOCKET_TIMEOUT = 0.1
MEMC_CONN_DELAY = 0.1
MEMC_CONN_MAX_RETRIES = 5
MEMC_QUEUE_SIZE = 0
MEMC_QUEUE_TIMEOUT = 1
MEMC_POOL_QUEUE_TIMEOUT = 0.2
CHUNK_DATA_SIZE = 50

RESULT_QUEUE_SIZE = 0
RESULT_QUEUE_TIMEOUT = None
NORMAL_ERR_RATE = 0.01

AppsInstalled = collections.namedtuple("AppsInstalled", ["dev_type", "dev_id", "lat", "lon", "apps"])


class MemcacheStore():
    def __init__(self, addr, max_retries, delay):
        self.conn = memcache.Client(addr, socket_timeout=MEMC_SOCKET_TIMEOUT)
        self.max_retries = max_retries
        self.delay = delay

    def set_multi(self, apps_packed):
        num_retries = 0
        while num_retries < self.max_retries:
            try:
                return self.conn.set_multi(apps_packed)
            except ConnectionError:
                self.conn()
                num_retries += 1
                time.sleep(self.delay)
        return None


class InsertApp(threading.Thread):
    def __init__(self, memc_pool_dict, memc_queue, res_queue):
        threading.Thread.__init__(self)
        self._memc_pool_dict = memc_pool_dict
        self._memc_queue = memc_queue
        self._res_queue = res_queue

    def run(self):
        processed = errors = 0
        while True:
            try:
                memc_addr, apps_packed, opt_dry = self._memc_queue.get(timeout=MEMC_QUEUE_TIMEOUT)
                ok = self.insert_appsinstalled(memc_addr, apps_packed, opt_dry)
                if ok:
                    processed += 1
                else:
                    errors += 1
            except queue.Empty:
                self._res_queue.put((processed, errors), timeout=RESULT_QUEUE_TIMEOUT)
                return

    def insert_appsinstalled(self, memc_addr, apps_packed, dry_run=False):

        try:
            if dry_run:
                for key in apps_packed.keys():
                    unpacked = appsinstalled_pb2.UserApps()
                    unpacked.ParseFromString(apps_packed[key])
                    logging.debug("%s - %s -> %s" % (memc_addr, key,  str(unpacked).replace("\n", " ")))
            else:
                try:
                    memc = self._memc_pool_dict[memc_addr].get(timeout=MEMC_POOL_QUEUE_TIMEOUT)
                except queue.Empty:
                    memc = MemcacheStore([memc_addr], MEMC_CONN_MAX_RETRIES, MEMC_CONN_DELAY)
                memc.set_multi(apps_packed)
                self._memc_pool_dict[memc_addr].put(memc)
        except Exception as e:
            logging.exception("Cannot write to memc %s: %s" % (memc_addr, e))
            return False
        return True


class ParseApp(threading.Thread):
    def __init__(self, memc_queue, res_queue, path, dev_memc, opt_dry):
        threading.Thread.__init__(self)
        self._memc_queue = memc_queue
        self._res_queue = res_queue
        self.path = path
        self.dev_memc = dev_memc
        self.dry = opt_dry

    @staticmethod
    def get_line_app_packed(appsinstalled):
        ua = appsinstalled_pb2.UserApps()
        ua.lat = appsinstalled.lat
        ua.lon = appsinstalled.lon
        key = "%s:%s" % (appsinstalled.dev_type, appsinstalled.dev_id)
        ua.apps.extend(appsinstalled.apps)
        packed = ua.SerializeToString()
        return {key: packed}

    def run(self):
        apps_packed_dict = {}
        for dev_type in self.dev_memc.keys():
            apps_packed_dict[dev_type] = {}
        processed = errors = 0
        logging.info('Processing %s' % self.path)
        with gzip.open(self.path) as fd:
            for line in fd:
                line = line.strip()
                if not line:
                    continue
                appsinstalled = self.parse_appsinstalled(line)
                if not appsinstalled:
                    errors += 1
                    continue
                dev_type = appsinstalled.dev_type
                memc_addr = self.dev_memc.get(dev_type)
                if not memc_addr:
                    errors += 1
                    logging.error("Unknown device type: %s" % appsinstalled.dev_type)
                    continue
                apps_packed_with_key = self.get_line_app_packed(appsinstalled)
                apps_packed_dict.get(dev_type).update(apps_packed_with_key)
                if len(apps_packed_dict.get(dev_type)) >= CHUNK_DATA_SIZE:
                    apps_packed = apps_packed_dict.get(dev_type)
                    memc_addr = self.dev_memc.get(dev_type)
                    self._memc_queue.put((memc_addr, apps_packed, self.dry))
                    apps_packed_dict[dev_type] = {}
        for dev_type in self.dev_memc.keys():
            apps_packed = apps_packed_dict.get(dev_type)
            memc_addr = self.dev_memc.get(dev_type)
            self._memc_queue.put((memc_addr, apps_packed, self.dry))
            apps_packed_dict[dev_type] = {}
        self._res_queue.put((processed, errors))

    @staticmethod
    def parse_appsinstalled(line):
        line_parts = line.decode('utf-8').strip().split('\t')
        if len(line_parts) < 5:
            return
        dev_type, dev_id, lat, lon, raw_apps = line_parts
        if not dev_type or not dev_id:
            return
        try:
            apps = [int(a.strip()) for a in raw_apps.split(",")]
        except ValueError:
            apps = [int(a.strip()) for a in raw_apps.split(",") if a.isidigit()]
            logging.info("Not all user apps are digits: `%s`" % line)
        try:
            lat, lon = float(lat), float(lon)
        except ValueError:
            logging.info("Invalid geo coords: `%s`" % line)
        return AppsInstalled(dev_type, dev_id, lat, lon, apps)


def dot_rename(path):
    head, fn = os.path.split(path)
    # atomic in most cases
    os.rename(path, os.path.join(head, "." + fn))


def run_thread_pool(memc_pool_dict, memc_queue, res_queue, size):
    threads = []
    for _ in range(size):
        thread = InsertApp(memc_pool_dict, memc_queue, res_queue)
        thread.start()
        threads.append(thread)
    return threads


def join_thread_pool(pool):
    for thread in pool:
        thread.join()


def run_process(fn, dev_memc, opt_dry):
    pid = os.getpid()
    logging.info("Process %d running." % (pid))
    memc_pool_dict = collections.defaultdict(queue.Queue)
    memc_queue = queue.Queue(MEMC_QUEUE_SIZE)
    res_queue = queue.Queue(RESULT_QUEUE_SIZE)
    thread = ParseApp(memc_queue, res_queue, fn, dev_memc, opt_dry)
    thread.start()
    pool = run_thread_pool(memc_pool_dict, memc_queue, res_queue, THREADS_IN_WORKER_COUNT)
    thread.join()
    join_thread_pool(pool)
    processed = errors = 0
    while not res_queue.empty():
        proc, err = res_queue.get(timeout=RESULT_QUEUE_TIMEOUT)
        processed += proc
        errors += err
    if not processed:
        dot_rename(fn)
        return fn
    err_rate = float(errors) / processed
    if err_rate < NORMAL_ERR_RATE:
        logging.info("Process %d: Acceptable error rate (%s). Successfull load" % (pid, err_rate))
    else:
        logging.error("Process %d: High error rate (%s > %s). Failed load" % (pid, err_rate, NORMAL_ERR_RATE))
    dot_rename(fn)
    return fn


def main(options):
    device_memc = {
        "idfa": options.idfa,
        "gaid": options.gaid,
        "adid": options.adid,
        "dvid": options.dvid,
    }
    path_list = sorted(list(glob.iglob(options.pattern)))
    with Pool(processes=WORKERS_COUNT) as pool:
        ps = pool.imap(partial(run_process, dev_memc=device_memc, opt_dry=options.dry), path_list)
        for p in ps:
            logging.info('Processing for %s finished' % p)


def prototest():
    sample = "idfa\t1rfw452y52g2gq4g\t55.55\t42.42\t1423,43,567,3,7,23\ngaid\t7rfw452y52g2gq4g\t55.55\t42.42\t7423,424"
    for line in sample.splitlines():
        dev_type, dev_id, lat, lon, raw_apps = line.strip().split("\t")
        apps = [int(a) for a in raw_apps.split(",") if a.isdigit()]
        lat, lon = float(lat), float(lon)
        ua = appsinstalled_pb2.UserApps()
        ua.lat = lat
        ua.lon = lon
        ua.apps.extend(apps)
        packed = ua.SerializeToString()
        unpacked = appsinstalled_pb2.UserApps()
        unpacked.ParseFromString(packed)
        assert ua == unpacked, "Test Failed"
    logging.info("Test OK")


if __name__ == '__main__':
    op = OptionParser()
    op.add_option("-t", "--test", action="store_true", default=False)
    op.add_option("-l", "--log", action="store", default=None)
    op.add_option("--dry", action="store_true", default=False)
    op.add_option("--pattern", action="store", default="data/*.tsv.gz")
    op.add_option("--idfa", action="store", default="127.0.0.1:33013")
    op.add_option("--gaid", action="store", default="127.0.0.1:33014")
    op.add_option("--adid", action="store", default="127.0.0.1:33015")
    op.add_option("--dvid", action="store", default="127.0.0.1:33016")
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO if not opts.dry else logging.DEBUG,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    if opts.test:
        prototest()
        sys.exit(0)

    logging.info("Memc loader started with options: %s" % opts)
    try:
        main(opts)
    except Exception as e:
        logging.exception("Unexpected error: %s" % e)
        sys.exit(1)
