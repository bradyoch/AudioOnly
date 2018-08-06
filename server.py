import socket

HOST = "127.0.0.1"
PORT = 9000

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

HTML_BODY_TEMP = ("<h1>Welcome to the server</h1>")

def get_request(conn):
    request = {}
    data = conn.recv(1024).decode().split("\r\n")

    request["Request"] = data[0]
    data = data[1:]

    for s in data:
        if not s:
            continue
        tag, info = s.split(":", 1)
        request[tag] = info

    return request

def server_connect():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(1)

        conn, addr = server.accept()
        with conn:
            print("Connection from: ", addr)
            request = get_request(conn)
            conn.sendall(RESPONSE_200.format(0).encode())

def main():
    server_connect()

if __name__ == "__main__":
    main()
