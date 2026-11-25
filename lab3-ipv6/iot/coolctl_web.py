#!/usr/bin/env python3
"""CoolCtl 3000 web interface (lab 3, stage 6): HTTP basic auth, default
credentials admin:admin. Serves /opt/iot/index.html with {{FLAG}} replaced
by env FLAG_LOGIN after a successful login."""
import base64
import os
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

USER, PASSWORD = "admin", "admin"
FLAG = os.environ.get("FLAG_LOGIN", "FLAG{unset}")
PAGE = open("/opt/iot/index.html", encoding="utf-8").read().replace("{{FLAG}}", FLAG).encode()
GOOD = "Basic " + base64.b64encode(f"{USER}:{PASSWORD}".encode()).decode()


class Handler(BaseHTTPRequestHandler):
    server_version = "CoolCtl-httpd/3.0"
    sys_version = ""

    def do_GET(self):
        if self.headers.get("Authorization") != GOOD:
            body = b"<h1>401 Unauthorized</h1><p>CoolCtl 3000: please log in.</p>"
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="CoolCtl 3000"')
        else:
            body = PAGE
            self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    do_HEAD = do_GET


class Server(ThreadingHTTPServer):
    address_family = socket.AF_INET6


print("[coolctl] web interface on [::]:80 (basic auth)", flush=True)
Server(("::", 80), Handler).serve_forever()
