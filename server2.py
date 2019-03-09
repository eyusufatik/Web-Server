import socket
import io
import sys

class WSGIServer:
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queu_size = 1

    def __init__(self, server_address):
        self.listen_socket = socket.socket(self.address_family,self.socket_type)
        self.listen_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.listen_socket.bind(server_address)
        self.listen_socket.listen(self.request_queu_size)
        host, port = self.listen_socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port
        self.headers_set = []

    def set_app(self, application):
        self.application = application

    def server_forever(self):
        while True:
            self.client_connection, self.client_address = self.listen_socket.accept()
            self.handle_one_request()

    def handle_one_request(self):
        self.request_data = self.client_connection.recv(1024)
