# -*- coding: utf-8 -*-

import logging
import mimetypes
import os
import socket
from time import strftime, gmtime
from urllib.parse import urlparse, unquote

PROTOCOL_TYPE = 'HTTP/1.1'
CHUNK_SIZE = 1024
HTTP_HEAD_TERMINATOR = b'\r\n\r\n'

ALLOWED_CONTENT_TYPES = (
    'text/css',
    'text/html',
    'application/javascript',
    'image/jpg',
    'image/jpeg',
    'image/png',
    'image/gif',
    'text/plain',
    'application/x-shockwave-flash'
)

ALLOWED_METHODS = (
    'HEAD',
    'GET'
)

OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
NOT_ALLOWED = 405

RESPONSE_STATUS_CODES = {
    OK: 'OK',
    BAD_REQUEST: 'Bad Request',
    NOT_FOUND: 'Not Found',
    FORBIDDEN: 'Forbidden',
    NOT_ALLOWED: 'Method Not Allowed',
}


class RequestHandler():
    def __init__(self, request, root_path, server_name):
        self.request = request
        self.root_path = root_path
        self.server_name = server_name
        self.method = None
        self.c_type = None
        self.resp_body = None
        self.c_length = 0

    def parse_request(self):
        req_list = self.request.split('\r\n')
        start_line = req_list[0].split()
        if len(start_line) != 3:
            return None
        method = start_line[0]
        url = start_line[1][1:] if len(start_line) > 1 else ''
        protocol = start_line[2] if len(start_line) > 2 else ''
        return method, url, protocol

    def get_path(self, url_raw):
        url = unquote(url_raw)
        parsed_url = urlparse(url).path
        path = os.path.join(self.root_path, os.path.normpath(parsed_url))
        if os.path.isdir(path):
            file = os.path.join(path, 'index.html')
            if not os.path.isfile(file):
                file = None
        elif os.path.isfile(path) and not parsed_url.endswith('/'):
            file = path
        else:
            file = None
        return file

    def request_handler(self):
        c_type = None
        resp_body = None
        if not self.parse_request():
            return BAD_REQUEST
        method, url, protocol = self.parse_request()
        fs = 0
        file = self.get_path(url)
        if method not in ALLOWED_METHODS:
            code = NOT_ALLOWED
        else:
            if not file:
                code = NOT_FOUND
            else:
                fs = os.path.getsize(file)
                try:
                    c_type, _ = mimetypes.guess_type(file)
                    if c_type not in ALLOWED_CONTENT_TYPES:
                        code = FORBIDDEN
                    else:
                        code, resp_body = self.open_file(file)
                except Exception as e:
                    code = NOT_FOUND
                    logging.exception(f'Exception {e}')
        self.c_type = c_type
        self.c_length = str(fs)
        self.resp_body = resp_body
        self.method = method
        return code

    def open_file(self, file):
        if self.method == 'HEAD':
            resp_body = None
            code = OK
        else:
            try:
                with open(file, 'rb') as f:
                    resp_body = f.read()
                    code = OK
            except Exception as e:
                code = NOT_FOUND
                resp_body = None
                logging.exception(f'Exception {e}')
        return code, resp_body

    def get_response_headers(self, code, c_type, c_length):
        headers = {}
        headers['Date'] = self.get_date_time()
        headers['Server'] = self.server_name
        if code != OK:
            headers['Content-Type'] = 'text/html; charset=utf-8'
            headers['Content-Length'] = 0
            headers['Connection'] = 'close'
        else:
            headers['Content-Type'] = c_type
            headers['Content-Length'] = c_length
            headers['Connection'] = 'close'
        resp_headers = '\r\n'.join('%s: %s' % (k, v) for k, v in headers.items())
        return resp_headers

    def create_response(self):
        code = self.request_handler()
        start_line = ''.join('%s %s %s' % (PROTOCOL_TYPE, code, RESPONSE_STATUS_CODES[code]))
        headers = self.get_response_headers(code, self.c_type, self.c_length)
        if code != OK or self.method == 'HEAD':
            response = (''.join('%s\r\n%s\r\n\r\n' % (start_line, headers))).encode('utf-8')
        else:
            response = (''.join('%s\r\n%s\r\n\r\n' % (start_line, headers))).encode('utf-8') + self.resp_body
        return response

    @staticmethod
    def get_date_time():
        return strftime('%a, %d %b %Y %H:%M:%S GMT', gmtime())


class TCPServer:
    def __init__(self, host, port, name, request_queue_size, client_timeout,
                 root_path, RequestHandlerClass,
                 address_family=socket.AF_INET,
                 socket_type=socket.SOCK_STREAM,
                 bind_and_activate=True):
        self.server_address = (host, port)
        self.addr_family = address_family
        self.server_name = name
        self.socket_type = socket_type
        self.request_queue_size = request_queue_size
        self.client_timeout = client_timeout
        self.root_path = root_path
        self.chunk_size = CHUNK_SIZE
        self._socket = None
        self.RequestHandlerClass = RequestHandlerClass
        if bind_and_activate:
            if self._socket:
                self._socket.close()
            self._socket = socket.socket(self.addr_family, self.socket_type)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.bind(self.server_address)
            self._socket.listen(self.request_queue_size)

    def connect(self):
        conn, addr = self._socket.accept()
        logging.info("Start server listening")
        return conn, addr

    def close(self):
        return self._socket.close()

    def recieve(self, client_socket):
        request_data = b''
        try:
            while True:
                curr_data = client_socket.recv(self.chunk_size)
                request_data += curr_data
                if request_data.find(HTTP_HEAD_TERMINATOR) >= 0 or not curr_data:
                    break
        except ConnectionError:
            pass
        return request_data

    def run_server(self):
        logging.basicConfig(filename=None,
                            format='[%(asctime)s] %(levelname).1s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.INFO)
        while True:
            client_socket, client_address = self.connect()
            client_socket.settimeout(self.client_timeout)
            with client_socket:
                raw_data = self.recieve(client_socket)
                logging.info(f'Received raw_request: {raw_data}')
                recv_data = raw_data.decode('utf-8')
                logging.info(f'Received request: {recv_data}')
                req_handler = self.RequestHandlerClass(recv_data, self.root_path, self.server_name)
                response = req_handler.create_response()
                logging.info(f'Send response: {response}')
                client_socket.sendall(response)
