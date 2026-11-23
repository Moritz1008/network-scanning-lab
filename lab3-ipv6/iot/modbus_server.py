#!/usr/bin/env python3
"""Minimal Modbus/TCP server for lab 3, stage 7. No dependencies.

Plays the CoolCorp cooling controller. Function codes:
  0x03/0x04 read holding/input registers
  0x11      report slave ID     (what nmap's modbus-discover asks by default)
  0x2B/0x0E read device identification (modbus-discover with aggressive=true)
The flag (env FLAG_MODBUS) is stored as ASCII, two characters per register,
starting at holding register 100 and padded with zeros.
"""
import os
import socket
import socketserver
import struct

FLAG = os.environ.get("FLAG_MODBUS", "FLAG{unset}").encode()
FLAG_START, FLAG_REGS = 100, 32

regs = [0] * 200
# 0: setpoint -18.2 C (x10, int16)  1: alarm off  2: compressor on  3: door closed
regs[0:4] = [(-182) & 0xFFFF, 0, 1, 0]
data = FLAG.ljust(FLAG_REGS * 2, b"\0")[:FLAG_REGS * 2]
for k in range(FLAG_REGS):
    regs[FLAG_START + k] = (data[2 * k] << 8) | data[2 * k + 1]

SLAVE_ID = (b"CoolCorp CoolCtl-Core cooling controller fw 2.1 - "
            b"maintenance token in holding registers 100-131 (ASCII)")
DEVICE_ID = [b"CoolCorp", b"CoolCtl-Core", b"2.1", b"https://coolcorp.invalid", b"CoolCtl-Core HQ cold room"]


def pdu_reply(fc, body):
    if fc in (3, 4) and len(body) >= 4:
        start, count = struct.unpack(">HH", body[:4])
        if not 1 <= count <= 125 or start + count > len(regs):
            return bytes([fc | 0x80, 2])
        vals = regs[start:start + count]
        return bytes([fc, 2 * count]) + struct.pack(">%dH" % count, *vals)
    if fc == 0x11:
        payload = SLAVE_ID  # device-specific data only, printed by modbus-discover
        return bytes([fc, len(payload)]) + payload
    if fc == 0x2B and body[:1] == b"\x0e":
        objs = b"".join(bytes([i, len(v)]) + v for i, v in enumerate(DEVICE_ID))
        return bytes([fc, 0x0E, 0x01, 0x01, 0x00, 0x00, len(DEVICE_ID)]) + objs
    return bytes([fc | 0x80, 1])  # illegal function


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        s = self.request
        while True:
            head = s.recv(7)
            if len(head) < 7:
                return
            tid, pid, length, unit = struct.unpack(">HHHB", head)
            pdu = b""
            while len(pdu) < length - 1:
                chunk = s.recv(length - 1 - len(pdu))
                if not chunk:
                    return
                pdu += chunk
            rep = pdu_reply(pdu[0], pdu[1:])
            s.sendall(struct.pack(">HHHB", tid, 0, len(rep) + 1, unit) + rep)


class Server(socketserver.ThreadingTCPServer):
    address_family = socket.AF_INET6
    allow_reuse_address = True
    daemon_threads = True


print("[modbus] listening on [::]:502", flush=True)
Server(("::", 502), Handler).serve_forever()
