# -*- coding: utf-8 -*-
import logging
import socket
import threading


class TCPThreadingServer:
    def __init__(self, host, port, request_queue_size, client_timeout, address_family=socket.AF_INET,
                 socket_type=socket.SOCK_STREAM,
                 bind_and_activate=True):
        self.server_address = (host, port)
        self.addr_family = address_family
        self.socket_type = socket_type
        self.request_queue_size = request_queue_size
        self.client_timeout = client_timeout
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
        request=client_socket.recv(1024).decode('utf-8')
        logging.info(f'Received request: {request}')
        response='hello'.encode('utf-8')
        header = 'HTTP/1.1 200 OK\n' + 'Content-Type: ' 'text/html' + '\n\n'
        client_socket.send(header.encode('utf-8')+response)
        print('ok')

    def run_server(self):
        while True:
            client_socket, client_address = self.accept()
            client_socket.settimeout(self.client_timeout)
            t = threading.Thread(
                target=self.request_handler,
                args=(client_socket,)
            )
            t.start()
