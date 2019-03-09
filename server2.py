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

    def serve_forever(self):
        while True:
            self.client_connection, self.client_address = self.listen_socket.accept()
            self.handle_one_request()

    def handle_one_request(self):
        self.request_data = self.client_connection.recv(1024).decode()
        print(''.join(
            '< {0}\n'.format(line)
            for line in self.request_data.splitlines()
        ))
        self.parse_request(self.request_data)
        env = self.get_environment()
        result = self.application(env, self.start_response)
        self.finish_response(result)
    
    def parse_request(self, text):
        request_line = text.splitlines()[0]
        request_line = request_line.rstrip()
        (self.request_method,  # GET
         self.path,            # /hello
         self.request_version  # HTTP/1.1
         ) = request_line.split()

    def get_environment(self):
        env = {}
        env['wsgi.version']      = (1, 0)
        env['wsgi.url_scheme']   = 'http'
        env['wsgi.input']        = io.StringIO(self.request_data)
        env['wsgi.errors']       = sys.stderr
        env['wsgi.multithread']  = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once']     = False
        # Required CGI variables
        env['REQUEST_METHOD']    = self.request_method    # GET
        env['PATH_INFO']         = self.path              # /hello
        env['SERVER_NAME']       = self.server_name       # localhost
        env['SERVER_PORT']       = str(self.server_port)  # 8888
        return env

    def start_response(self, status, response_headers, exc_info = None):
        server_headers = [
            ('Date', 'Tue, 9 Mar 2018 20:02:21 GMT'),
            ('Server', 'WSGIServer 0.2'),
        ]
        self.headers_set = [status, response_headers + server_headers]

    def finish_response(self, result):
        try:
            status, response_headers = self.headers_set
            response = 'HTTP/1.1 {0}\r\n'.format(status)
            for header in response_headers:
                response += '{0}: {1}\r\n'.format(*header)
            response += "\r\n"
            for data in result:
                response += data.decode()
            print(''.join(
                    '> {line}\n'.format(line=line)
                    for line in response.splitlines()
            ))
            self.client_connection.sendall(response.encode())
        finally:
            self.client_connection.close()

SERVER_ADDRESS = (HOST, PORT) = '', 8888

def make_server(server_address, application):
    server = WSGIServer(server_address)
    server.set_app(application)
    return server

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Provide a WSGI application object as module:callable')
        exit()
    app_path = sys.argv[1]
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module, application)
    httpd = make_server(SERVER_ADDRESS, application)
    print('WSGIServer: Serving HTTP on port {port} ...\n'.format(port=PORT))
    httpd.serve_forever()

