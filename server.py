import socket, os

HOST = "127.0.0.1"
PORT = 9000

SERVER_ROOT = "www/"

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

    def parse_request(self, data):
        data = data.decode().split("\r\n")
        self.command, self.file, _ = data[0].split()
        
        self.misc = data[1:]

def server_connect():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(1)

        conn, addr = server.accept()
        with conn:
            print("Connection from: ", addr)
            request = Request()
            request.parse_request(conn.recv(1024))
            
            print(request.command, request.file)
            if request.command != "GET":
                conn.sendall(RESPONSE_400.encode())
                return

            if request.file == "/":
                request.file == "/index.html"
            print(request.file)
            request.file = SERVER_ROOT + request.file

            with open(request.file, "rb") as f:
                file_len = os.fstat(f.fileno()).st_size
                conn.sendall(RESPONSE_200.format(file_len).encode())
                conn.sendfile(f)

def main():
    server_connect()

if __name__ == "__main__":
    main()
