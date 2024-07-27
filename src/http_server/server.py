import socket
import sys
import threading
from email.message import Message
from email.parser import Parser
from functools import lru_cache
from io import BufferedReader
from typing import Any
from urllib.parse import parse_qs, urlparse

HOST = "localhost"
PORT = 8080
MAX_LINE = 64 * 1024
MAX_HEADERS = 100


class HTTPError(Exception):
    def __init__(self, status: int, reason: str, body: Any = None) -> None:
        super()
        self.status = status
        self.reason = reason
        self.body = body


class Request:
    def __init__(
        self,
        method: Any,
        target: Any,
        version: Any,
        headers: Message,
        rfile: BufferedReader,
    ) -> None:
        self.method = method
        self.target = target
        self.version = version
        self.headers = headers
        self.rfile = rfile

    @property
    def path(self) -> Any:
        return self.url.path

    @property
    @lru_cache(maxsize=None)
    def query(self) -> dict:
        return parse_qs(self.url.query)

    @property
    @lru_cache(maxsize=None)
    def url(self) -> Any:
        return urlparse(self.target)

    def body(self) -> Any:
        size = self.headers.get("Content-Length")
        if not size:
            return None
        return self.rfile.read(size)


class Response:
    def __init__(self, status: int, reason: str, headers: Any = None, body: Any = None) -> None:
        self.status = status
        self.reason = reason
        self.headers = headers
        self.body = body


def handle_request(client_socket: socket.socket) -> None:
    try:
        req = parse_request(client_socket)
        resp = handle_method(req)
        send_response(client_socket, resp)
    except Exception as e:
        print(e)
    finally:
        client_socket.close()


def handle_method(req: "Request") -> "Response":
    if req.path == "/" and req.method == "GET":
        return handle_get(req)
    if req.path == "/" and req.method == "HEAD":
        return handle_head(req)
    raise HTTPError(404, "Not found")


def handle_get(req: "Request") -> "Response":
    accept = str(req.headers.get("Accept"))
    if "text/html" in accept:
        contentType = "text/html; charset=utf-8"
        body = "<html><head></head><body>"
        body += "<div>Пользователи (10)</div>"
        body += "</body></html>"
    else:
        return Response(406, "Not Acceptable")

    body = body.encode("utf-8")  # type: ignore
    headers = [("Content-Type", contentType), ("Content-Length", len(body))]
    return Response(200, "OK", headers, body)


def handle_head(req: "Request") -> "Response":
    accept = str(req.headers.get("Accept"))
    if "text/html" in accept:
        contentType = "text/html; charset=utf-8"
    else:
        return Response(406, "Not Acceptable")

    headers = [
        ("Content-Type", contentType),
    ]
    return Response(200, "OK", headers, None)


def parse_request(conn: socket.socket) -> "Request":
    rfile = conn.makefile("rb")
    method, target, ver = parse_request_line(rfile)
    headers = parse_headers(rfile)
    host = headers.get("Host")
    if not host:
        raise HTTPError(400, "Bad request", "Host header is missing")
    if host not in (f"{HOST}:{PORT}"):
        raise HTTPError(404, "Not found")
    return Request(method, target, ver, headers, rfile)


def parse_request_line(rfile: BufferedReader) -> tuple:
    raw = rfile.readline(MAX_LINE + 1)
    if len(raw) > MAX_LINE:
        raise HTTPError(400, "Bad request", "Request line is too long")

    req_line = str(raw, "iso-8859-1")
    words = req_line.split()
    if len(words) != 3:
        raise HTTPError(400, "Bad request", "Malformed request line")

    method, target, ver = words
    if ver != "HTTP/1.1":
        raise HTTPError(505, "HTTP Version Not Supported")
    return method, target, ver


def send_response(conn: socket.socket, resp: Response) -> None:
    wfile = conn.makefile("wb")
    status_line = f"HTTP/1.1 {resp.status} {resp.reason}\r\n"
    wfile.write(status_line.encode("iso-8859-1"))

    if resp.headers:
        for key, value in resp.headers:
            header_line = f"{key}: {value}\r\n"
            wfile.write(header_line.encode("iso-8859-1"))

    wfile.write(b"\r\n")

    if resp.body:
        wfile.write(resp.body)

    wfile.flush()
    wfile.close()


def parse_headers(rfile: BufferedReader) -> Any:
    headers = []
    while True:
        line = rfile.readline(MAX_LINE + 1)
        if len(line) > MAX_LINE:
            raise HTTPError(494, "Request header too large")

        if line in (b"\r\n", b"\n", b""):
            break

        headers.append(line)
        if len(headers) > MAX_HEADERS:
            raise HTTPError(494, "Too many headers")

    sheaders = b"".join(headers).decode("iso-8859-1")
    return Parser().parsestr(sheaders)


def start_server() -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
    server_address = (HOST, PORT)
    client_socket.bind((server_address))
    client_socket.listen()
    while True:
        try:
            client_socket, _ = client_socket.accept()
        except OSError:
            pass
        client_handler = threading.Thread(target=handle_request, args=(client_socket,))
        client_handler.start()


if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        sys.exit(0)
