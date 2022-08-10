# -*- coding: utf-8 -*-
import logging
import mimetypes
import os
import socket
import threading
from time import strftime, gmtime

ALLOWED_CONTENT_TYPES = (
    'text/css',
    'text/html',
    'application/javascript',
    'image/jpg',
    'image/jpeg',
    'image/png',
    'image/gif',
    'application/x-shockwave-flash'
)


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

    def request_handler(self, client_socket):
        req = {}
        headers = {}
        protocol_type = 'HTTP/1.1'
        headers['Content-Type'] = 'text/html;charset=utf-8'
        request = client_socket.recv(1024)
        logging.info(f'Received request: {request}')
        request = request.decode('utf-8')
        req_list = request.split('\r\n')
        print(req_list)
        req_start_line = req_list[0].split(' ')
        req['method'] = req_start_line[0]
        while '%20' in req_start_line[1]:
            req_start_line[1]=req_start_line[1].replace('%20', '')
            print(req_start_line[1])
        req['url'] = req_start_line[1][1:]
        req['protocol'] = req_start_line[2]
        print(f'req: {req}')
        if req['protocol'] != 'HTTP/1.1':
            status_code = '505 HTTP Version Not Supported'
            message_body='<html>505 HTTP Version Not Supported</html>'
        else:
            if req['method'] != 'GET' and req['method'] != 'HEAD':
                status_code = '405 Method Not Allowed'
                message_body = '<html>405 Method Not Allowed</html>'
            else:
                path=os.path.join(self.root_path, req['url'])
                if req['url'] == '':
                    file = os.path.join(self.root_path, 'index.html')
                elif '.' in req['url'] and os.path.isfile(path):
                    file = path
                elif os.path.isdir(path):
                    file = os.path.join(path,'index.html')
                else:
                    file=None
                headers['Date'] = self.get_date_time()
                headers['Server'] = self.server_name
                headers['Connection'] = 'keep-alive'
                print(f'file: {file}')
                if not file:
                    status_code = '404 Not Found'
                    message_body = '<html>404 Not Found</html>'
                else:
                    try:
                        with open(file, 'rb') as f:
                            message_body = f.read().decode('utf-8')
                    except Exception as e:
                        status_code = '404 Not Found'
                        message_body = '<html>404 Not Found</html>'
                        logging.exception(f'Exception {e}')
                    else:
                        try:
                            (content_type, _) = mimetypes.guess_type(file)
                            if content_type not in ALLOWED_CONTENT_TYPES:
                                status_code = '405 Method Not Allowed'
                                message_body = '<html>405 Method Not Allowed</html>'
                            else:
                                headers['Content-Type'] = content_type
                                status_code = '200 OK'
                                file_size = os.path.getsize(file)
                                headers['Content-Length'] = file_size
                        except Exception as e:
                            status_code = '404 Not Found'
                            message_body = '<html>404 Not Found</html>'
                            logging.exception(f'Exception {e}')
                if req['method'] == 'HEAD':
                    headers['Content-Length'] = 0
                    message_body = None
        start_line = ''.join('%s %s' % (protocol_type, status_code))
        print('start_line:', start_line)
        print('headers:', headers)
        print('message_body:', message_body)
        headers = '\r\n'.join('%s: %s' % (k, v) for k, v in headers.items())
        response = ''.join('%s\r\n%s\r\n\r\n%s' % (start_line, headers, message_body))
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
