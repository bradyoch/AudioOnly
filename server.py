#!/usr/bin/env python3

import socket, os, re

HOST = "127.0.0.1"
PORT = 9000

SERVER_ROOT = "www/"
URL_REGEX = ("^((https{0,1}://){0,1}(youtu.be/|www.youtube.com/watch\?v=)){0,1}"
             "([a-zA-Z0-9_]{11})$")

# use conn.sendfile after sending this response
RESPONSE_200 = ("HTTP/1.1 200 OK\r\n"
                "Content-type: text/html\r\n"
                "Content-length: {}\r\n\r\n")

RESPONSE_400 = ("HTTP/1.1 400 Bad Request\r\n"
                "Content-type: text/html\r\n"
                "Content-legth: 11\r\n\r\n"
                "Bad Request")

RESPONSE_404 = ("HTTP/1.1 404 Not Found\r\n"
                "Content-type: text/plain\r\n"
                "Content-length: 9\r\n\r\n"
                "Not Found")

class Request():
    def __init__(self):
        self.command = ""
        self.file = ""
        self.misc = []
        self.args = ""

    def parse_request(self, data):
        data = data.decode().split("\r\n")
        self.command, self.file, _ = data[0].split()

        self.misc = data[1:-1]
        self.args = data[-1]
        print("Command: {} Path: {}".format(self.command, self.file))

        if self.file == "/":
            self.file += "index.html"
        self.file = SERVER_ROOT + self.file

        while "%" in self.args:
            i = self.args.index("%")
            self.args = self.args[:i] \
                    + chr(int(self.args[i+1:i+3], 16)) \
                    + self.args[i+3:]

def handle_get(conn, file):
    try:
        with open(file, "rb") as f:
            file_len = os.fstat(f.fileno()).st_size
            conn.sendall(RESPONSE_200.format(file_len).encode())
            conn.sendfile(f)
    except FileNotFoundError as err:
        conn.sendall(RESPONSE_400.encode())
        print(err)

def handle_post(conn, args):
    args = [tuple(x.split("=", 1)) for x in args.split("&")]
    match = None

    for pair in args:
        if pair[0] == "url":
            match = re.fullmatch(URL_REGEX, pair[1])
            if not match:
                break

    if match:
        print("Request URL: ", match.groups())
        handle_get(conn, SERVER_ROOT + "index.html")
    else:
        conn.sendall(RESPONSE_400.encode())

def handle_connection(conn):
    request = Request()
    while True:
        request.parse_request(conn.recv(1024))

        if request.command == "GET":
            handle_get(conn, request.file)
        elif request.command == "POST":
            handle_post(conn, request.args)
            return

    conn.close()

def server_connect():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(1)

        conn, addr = server.accept()
        print("Connection from", addr)
        handle_connection(conn)

def main():
    server_connect()

if __name__ == "__main__":
    main()
