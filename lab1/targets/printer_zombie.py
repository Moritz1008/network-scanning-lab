#!/usr/bin/env python3
"""CoolCorp network printer - the idle-scan zombie.

Modern Linux kernels randomise or zero the IP ID field, which makes a stock
container useless as an idle-scan "zombie" (nmap reports "IP ID sequence class:
All zeros"). This userspace stack imitates a legacy JetDirect printer: it
answers every probe itself with a SINGLE GLOBAL, strictly incrementing IP ID -
exactly the predictable side channel `nmap -sI` needs.

Requirements (set in compose): cap_add NET_RAW + NET_ADMIN, and the kernel's own
RST packets dropped (iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP) so
only this stack replies. All TCP ports look closed; the only observable signal
is the IP ID, which ticks up by one for every SYN/ACK the printer is made to
answer - i.e. once per open port the idle scan probes on the real target.
"""
import itertools
import threading

from scapy.all import IP, TCP, Ether, conf, get_if_hwaddr, sendp, sniff

conf.verb = 0
IFACE = conf.iface
MAC = get_if_hwaddr(IFACE)

_counter = itertools.count(1)
_lock = threading.Lock()


def next_ip_id():
    with _lock:
        return next(_counter) & 0xFFFF


def handle(pkt):
    if Ether not in pkt or IP not in pkt or TCP not in pkt:
        return
    ip, tcp = pkt[IP], pkt[TCP]
    flags = int(tcp.flags)
    syn, ack, rst = flags & 0x02, flags & 0x10, flags & 0x04
    if rst:
        return  # never answer a RST
    if syn and ack:
        # Unsolicited SYN/ACK (idle scan induces these) -> RST, ID ticks up.
        reply = IP(src=ip.dst, dst=ip.src, id=next_ip_id()) / \
            TCP(sport=tcp.dport, dport=tcp.sport, flags="R", seq=tcp.ack)
    elif syn and not ack:
        # Someone probes the printer directly -> look like a closed port.
        reply = IP(src=ip.dst, dst=ip.src, id=next_ip_id()) / \
            TCP(sport=tcp.dport, dport=tcp.sport, flags="RA", seq=0, ack=tcp.seq + 1)
    else:
        return
    sendp(Ether(src=MAC, dst=pkt[Ether].src) / reply, iface=IFACE)


print(f"[printer] JetDirect zombie up on {IFACE} ({MAC}); "
      "global incremental IP ID counter started", flush=True)
sniff(filter="tcp", prn=handle, store=0, iface=IFACE)
