# -*- coding: utf-8 -*-
import logging
import mimetypes
import os
import socket
import threading
from time import strftime, gmtime

PROTOCOL_TYPE = 'HTTP/1.1'

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


class TCPThreadingServer:
    def __init__(self, host, port, name, request_queue_size, client_timeout, root_path, address_family=socket.AF_INET,
                 socket_type=socket.SOCK_STREAM,
                 bind_and_activate=True):
        self.server_address = (host, port)
        self.server_name = name
        self.addr_family = address_family
        self.socket_type = socket_type
        self.request_queue_size = request_queue_size
        self.client_timeout = client_timeout
        self.root_path = root_path
        self._socket = None
        if bind_and_activate:
            if self._socket:
                self._socket.close()
            self._socket = socket.socket(self.addr_family, self.socket_type)
            self._socket.bind(self.server_address)
            self._socket.listen(self.request_queue_size)

    def accept(self):
        return self._socket.accept()

    def parse_request(self, request):
        req_list = request.split('\r\n')
        print(req_list)
        req_start_line = req_list[0].split(' ')
        self.method = req_start_line[0]
        while '%20' in req_start_line[1]:
            req_start_line[1] = req_start_line[1].replace('%20', '')
            print(req_start_line[1])
        self.url = req_start_line[1][1:]
        self.protocol = req_start_line[2]

    def get_path(self, url):
        path = os.path.join(self.root_path, url)
        if url == '':
            file = os.path.join(self.root_path, 'index.html')
        elif '.' in url and os.path.isfile(path):
            file = path
        elif os.path.isdir(path):
            file = os.path.join(path, 'index.html')
        else:
            file = None
        return file

    def get_response_headers(self, code, type, length):
        headers = {}
        if code != OK:
            headers['Content-Type'] = 'text/html; charset=utf-8'
            headers['Content-Length'] = 0
            headers['Connection'] = 'close'
        else:
            # if self.method == 'HEAD':
            #     headers['Content-Length'] = 0
            #     headers['Connection'] = 'keep-alive'
            # else:
            headers['Date'] = self.get_date_time()
            headers['Server'] = self.server_name
            headers['Content-Type'] = type
            headers['Content-Length'] = length
            if self.method == 'GET':
                headers['Connection'] = 'keep-alive'
            if self.method == 'HEAD':
                headers['Connection'] = 'close'
        return headers

    def request_handler(self, client_socket):
        c_type = None
        c_length = 0
        response_body = None
        request = client_socket.recv(1024)
        logging.info(f'Received request: {request}')
        request = request.decode('utf-8')
        self.parse_request(request)
        file = self.get_path(self.url)
        if self.method != 'GET' and self.method != 'HEAD':
            status_code = NOT_ALLOWED
        else:
            if not file:
                status_code = NOT_FOUND
            else:
                try:
                    with open(file, 'rb') as f:
                        response_body = f.read()
                except Exception as e:
                    status_code = NOT_FOUND
                    logging.exception(f'Exception {e}')
                else:
                    try:
                        c_type, _ = mimetypes.guess_type(file)
                        if c_type not in ALLOWED_CONTENT_TYPES:
                            status_code = NOT_ALLOWED
                        else:
                            status_code = OK
                            c_length = os.path.getsize(file)
                    except Exception as e:
                        status_code = NOT_FOUND
                        logging.exception(f'Exception {e}')
        headers = self.get_response_headers(status_code, c_type, c_length)
        start_line = ''.join('%s %s %s' % (PROTOCOL_TYPE, status_code,RESPONSE_STATUS_CODES[status_code] ))
        headers = '\r\n'.join('%s: %s' % (k, v) for k, v in headers.items())
        if self.method =='HEAD':
            response = ''.join('%s\r\n%s\r\n\r\n' % (start_line, headers))
        else:
            response = ''.join('%s\r\n%s\r\n\r\n%s' % (start_line, headers, response_body))
        # print(response)
        client_socket.send(response.encode('utf-8'))

    @staticmethod
    def get_date_time():
        return strftime('%a, %d %b %Y %H:%M:%S GMT', gmtime())

    def run_server(self):
        while True:
            client_socket, client_address = self.accept()
            client_socket.settimeout(self.client_timeout)
            t = threading.Thread(
                target=self.request_handler,
                args=(client_socket,)
            )
            t.daemon = True
            t.start()
