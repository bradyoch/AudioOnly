#!/usr/bin/env python3

import os, re, socket, subprocess

HOST = "127.0.0.1"
PORT = 9000

SERVER_ROOT = "www/"
URL_REGEX = ("^((https{0,1}://){0,1}(youtu.be/|www.youtube.com/watch\?v=)){0,1}"
             "([a-zA-Z0-9_\-]{11})$")

# use conn.sendfile after sending this response
RESPONSE_200 = ("HTTP/1.1 200 OK\r\n"
                "Content-type: {}\r\n"
                "Content-length: {}\r\n\r\n")

RESPONSE_400 = ("HTTP/1.1 400 Bad Request\r\n"
                "Content-type: text/html\r\n"
                "Content-legth: 11\r\n\r\n"
                "Bad Request")

RESPONSE_404 = ("HTTP/1.1 404 Not Found\r\n"
                "Content-type: text/plain\r\n"
                "Content-length: 9\r\n\r\n"
                "Not Found")

CONTENT_TYPE = {"html": "text/html",
                "m4a" : "audio/m4a",
                "mp3" : "audio/mp3"}

class Request():
    def __init__(self):
        self.command = ""
        self.file = ""
        self.misc = []
        self.args = ""

    def parse_request(self, data):
        data = data.decode().split("\r\n")
        if not data:
            return

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
            conn.sendall(RESPONSE_200.format( \
                CONTENT_TYPE["html"], file_len).encode())
            conn.sendfile(f)
    except FileNotFoundError as err:
        conn.sendall(RESPONSE_400.encode())
        print(err)

def handle_post(conn, args):
    args = [tuple(x.split("=", 1)) for x in args.split("&")]
    match = None

    for pair in args:
        if pair[0] == "url":
            match = re.match(URL_REGEX, pair[1])
            if not match:
                return None

    video_code = match.groups()[-1]

    return video_code

def clean_cache(cache_dir, size):
    dir_size = len(cache_dir)
    if dir_size >= 10:
        oldest_name = cache_dir[0]
        oldest_time = os.stat("cache/" + oldest_name).st_atime

        for i in range(1, dir_size):
            stat = os.stat("cache/" + cache_dir[i])

            if stat.st_atime < oldest_time:
                oldest_name = cache_dir[i]
                oldest_time = stat.st_atime

    os.remove("cache/" + oldest_name)

def fetch_video(conn, vid_code):
    cache_dir = os.listdir("cache/")

    if not (vid_code + ".mp3" in cache_dir):
        clean_cache(cache_dir, 10)

        subprocess.run(["./youtube-dl", "-x", \
                        "--audio-format", "mp3", \
                        "-o", "cache/%(id)s.%(ext)s", \
                        vid_code])

    with open("cache/{}.mp3".format(vid_code), "rb") as f:
        file_len = os.fstat(f.fileno()).st_size
        conn.sendall(RESPONSE_200.format(
            CONTENT_TYPE["mp3"], file_len).encode())
        conn.sendfile(f)

def handle_connection(conn):
    request = Request()
    vid_code = ""

    while True:
        request.parse_request(conn.recv(1024))

        if request.command == "GET":
            handle_get(conn, request.file)
        elif request.command == "POST":
            vid_code = handle_post(conn, request.args)
            if vid_code:
                fetch_video(conn, vid_code)
            break

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
