#!/usr/bin/env python3
"""Tiny IPv6 TCP banner service for lab 3 corp hosts.

usage: banner.py PORT TEXT [PORT TEXT ...]

Sends TEXT to every client and closes. Backslash escapes in TEXT (\\r, \\n)
are interpreted, so banners can be written in one line in compose.yaml.
"""
import socket
import socketserver
import sys
import threading


class Server(socketserver.ThreadingTCPServer):
    address_family = socket.AF_INET6
    allow_reuse_address = True
    daemon_threads = True


def serve(port, text):
    data = text.encode().decode("unicode_escape").encode("latin-1")

    class Handler(socketserver.BaseRequestHandler):
        def handle(self):
            try:
                self.request.sendall(data)
            except OSError:
                pass

    Server(("::", port), Handler).serve_forever()


args = sys.argv[1:]
if not args or len(args) % 2:
    sys.exit(__doc__)
pairs = [(int(args[i]), args[i + 1]) for i in range(0, len(args), 2)]
for port, text in pairs:
    print(f"[banner] listening on [::]:{port}", flush=True)
    threading.Thread(target=serve, args=(port, text), daemon=True).start()
threading.Event().wait()
