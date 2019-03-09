import socket

host = ""
port = 8080

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((host,port))
listen_socket.listen(1)
print("HTTP server started. Listenening on {0}:{1}.".format(host,port))

while True:
    client_connection, client_address = listen_socket.accept()
    message = client_connection.recv(1024)
    print(message)

    http_response = """\
        HTTP/1.1 200 OK

        Hello, World!"""
    client_connection.sendall(http_response)
    client_connection.close()
