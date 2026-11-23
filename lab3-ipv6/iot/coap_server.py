#!/usr/bin/env python3
"""Minimal CoAP server (RFC 7252) for lab 3, stage 7. No dependencies.

Supports GET with piggybacked responses for CON and NON requests and the
/.well-known/core discovery resource (RFC 6690), which nmap's
coap-resources script reads. Flag comes from env FLAG_COAP.
"""
import os
import socket

FLAG = os.environ.get("FLAG_COAP", "FLAG{unset}")

RESOURCES = {
    "sensors/temp": (0, "-18.2 C"),
    "sensors/humidity": (0, "41 %"),
    "sensors/door": (0, "closed"),
    "maintenance/token": (0, "STAGE 7 CoAP FLAG: " + FLAG),
}
CORE = ",".join([
    '</sensors/temp>;rt="temperature-c";ct=0',
    '</sensors/humidity>;rt="humidity";ct=0',
    '</sensors/door>;rt="door-state";ct=0',
    '</maintenance/token>;title="maintenance access token";ct=0',
])
RESOURCES[".well-known/core"] = (40, CORE)  # 40 = application/link-format


def parse(data):
    if len(data) < 4 or data[0] >> 6 != 1:
        return None
    typ, tkl, code, mid = (data[0] >> 4) & 3, data[0] & 0xF, data[1], data[2:4]
    token = data[4:4 + tkl]
    i, opt, path = 4 + tkl, 0, []
    while i < len(data) and data[i] != 0xFF:
        delta, length = data[i] >> 4, data[i] & 0xF
        i += 1
        for which in ("d", "l"):
            v = delta if which == "d" else length
            if v == 13:
                v = data[i] + 13; i += 1
            elif v == 14:
                v = int.from_bytes(data[i:i + 2], "big") + 269; i += 2
            if which == "d":
                delta = v
            else:
                length = v
        opt += delta
        if opt == 11:  # Uri-Path
            path.append(data[i:i + length].decode(errors="replace"))
        i += length
    return typ, code, mid, token, "/".join(path)


def option(number, prev, value):
    delta = number - prev
    head = bytes([(delta << 4) | len(value)]) if len(value) < 13 else \
        bytes([(delta << 4) | 13, len(value) - 13])
    return head + value


def respond(typ, code, mid, token, payload=b"", ct=None):
    rtype = 2 if typ == 0 else 1  # CON -> ACK, NON -> NON
    out = bytes([0x40 | (rtype << 4) | len(token), code]) + mid + token
    if ct is not None:
        out += option(12, 0, bytes([ct]) if ct else b"")  # Content-Format
    if payload:
        out += b"\xff" + payload
    return out


sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
sock.bind(("::", 5683))
print("[coap] listening on [::]:5683 (udp)", flush=True)
while True:
    data, addr = sock.recvfrom(2048)
    req = parse(data)
    if not req:
        continue
    typ, code, mid, token, path = req
    if typ not in (0, 1):
        continue  # ignore ACK/RST
    if code != 1:  # only GET
        sock.sendto(respond(typ, 0x85, mid, token), addr)  # 4.05
    elif path in RESOURCES:
        ct, body = RESOURCES[path]
        sock.sendto(respond(typ, 0x45, mid, token, body.encode(), ct), addr)  # 2.05
    else:
        sock.sendto(respond(typ, 0x84, mid, token), addr)  # 4.04
