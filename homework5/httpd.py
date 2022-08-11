#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import argparse
import os

from server import TCPThreadingServer

from multiprocessing import Process

SERVER_HOST = 'localhost'
SERVER_PORT = 8080
SERVER_NAME = 'TCPServer'
SERVER_REQUEST_QUEUE_SIZE = 5
CLIENT_TIMEOUT = 10
DEFAULT_DOCUMENT_ROOT_PATH = '.'


def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"argument {path} is not a valid path")


def get_args():
    # parse the command line to get args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p',
        '--port',
        default=SERVER_PORT,
        help='Path to document root',
        type=int
    )
    parser.add_argument(
        '-r',
        '--root_path',
        default=DEFAULT_DOCUMENT_ROOT_PATH,
        help='Path to document root',
        type=dir_path
    )
    parser.add_argument(
        '-w',
        '--workers',
        default=1,
        help='workers count',
        type=int
    )
    args = parser.parse_args()
    workers_count = args.workers if args.workers > 0 else 1
    return (args.port, args.root_path, args.workers)


def logging_init(logging_file):
    # initialize script logging
    logging.basicConfig(filename=logging_file,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)


def run_workers(workers, run_server):
    workers = []
    try:
        for _ in range(workers_count):
            worker = Process(target=run_server)
            worker.start()
            logging.info("Server running on the process %d", worker.pid)
            workers.append(worker)
        for worker in workers:
            worker.join()
    except KeyboardInterrupt:
        for worker in workers:
            worker.terminate()
            logging.info("Process %d was terminated ", worker.pid)
        logging.exception('Interrupted by user')


if __name__ == '__main__':
    logging_init(None)
    port, root_path, workers_count = get_args()
    server = TCPThreadingServer(
        SERVER_HOST,
        port,
        SERVER_NAME,
        SERVER_REQUEST_QUEUE_SIZE,
        CLIENT_TIMEOUT,
        root_path
    )
    logging.info("Start server listening")
    try:
        run_workers(workers_count, server.run_server)
    except Exception:
        logging.exception("Unexpected error occurred")
        raise
    finally:
        logging.info("All done")
