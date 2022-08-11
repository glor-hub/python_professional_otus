# -*- coding: utf-8 -*-
import logging
import mimetypes
import os
import socket
import threading
from time import strftime, gmtime
from urllib.parse import urlparse, unquote

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

    def close(self):
        return self._socket.close()


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

    def get_path(self, url_raw):
        url=unquote(url_raw).replace(' ','')
        parsed_url=urlparse(url)
        path=parsed_url.path
        # query=parsed_url.query
        if path == '':
            file = os.path.join(self.root_path, 'index.html')
        elif os.path.isfile(path):
            file = os.path.join(self.root_path, path)
        elif os.path.isdir(path):
            path = os.path.join(self.root_path, path)
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
            headers['Date'] = self.get_date_time()
            headers['Server'] = self.server_name
            headers['Content-Type'] = type
            headers['Content-Length'] = length
            headers['Connection'] = 'keep-alive'
        return headers

    def get_response(self):
        if self.status_code != OK or self.method=='HEAD':
            response = ''.join('%s\r\n%s\r\n\r\n' % (self.start_line, self.headers))
        else:
            response = ''.join('%s\r\n%s\r\n\r\n%s' % (self.start_line, self.headers, self.response_body))
        return response

    def request_handler(self, client_socket):
        c_type = None
        c_length = 0
        resp_body = None
        request = client_socket.recv(1024)
        logging.info(f'Received request: {request}')
        request = request.decode('utf-8')
        self.parse_request(request)
        file = self.get_path(self.url)
        if self.method != 'GET' and self.method != 'HEAD':
            code = NOT_ALLOWED
        else:
            if not file:
                code = NOT_FOUND
            else:
                try:
                    with open(file, 'rb') as f:
                        resp_body = f.read()
                except Exception as e:
                    code = NOT_FOUND
                    logging.exception(f'Exception {e}')
                else:
                    try:
                        c_type, _ = mimetypes.guess_type(file)
                        if c_type not in ALLOWED_CONTENT_TYPES:
                            code = NOT_ALLOWED
                        else:
                            code = OK
                            c_length = os.path.getsize(file)
                    except Exception as e:
                        code = NOT_FOUND
                        logging.exception(f'Exception {e}')
        headers = self.get_response_headers(code, c_type, c_length)
        self.start_line = ''.join('%s %s %s' % (PROTOCOL_TYPE, code,RESPONSE_STATUS_CODES[status_code] ))
        self.status_code=code
        self.headers = '\r\n'.join('%s: %s' % (k, v) for k, v in headers.items())
        self.response_body=resp_body
        response = self.get_response()
        print(response)
        client_socket.send(response.encode('utf-8'))

    @staticmethod
    def get_date_time():
        return strftime('%a, %d %b %Y %H:%M:%S GMT', gmtime())

    def run_server(self):
        while True:
            try:
                client_socket, client_address = self.accept()
                client_socket.settimeout(self.client_timeout)
                t = threading.Thread(
                    target=self.request_handler,
                    args=(client_socket,)
                )
                t.daemon = True
                t.start()
                logging.info("Request handler running on the tread %d", t.name)
            except socket.error:
                self.close()
