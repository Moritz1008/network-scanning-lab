# Lab 3 – Hints


## Stage 3

`curl 'http://[fd00:c::80]/'` and read the HTML source, including comments.
Then try the addresses around the leaked one, e.g. `fd00:c::1000` to
`fd00:c::10ff`, with the same `-sn` then port scan approach as stage 2.

## Stage 4

Start at `0.0.0.0.0.0.0.0.c.0.0.0.0.0.d.f.ip6.arpa` and try all 16 nibbles
(`0`–`f`) in front of it. Follow every one that answers `NOERROR`, until you
are 32 nibbles deep; there `dig … PTR +short` gives you the name. A recursive
shell function or `atk6-dnsrevenum6 fd00:6:6::53 fd00:c::/64` does the work.
Turn the nibbles around again to get the address.

## Stage 5

You know the router as `fd00:6:6::fe` (stage 1) and you saw `172.30.0.254`
in the IPv4 sweep (stage 0). Compare `nmap -4 -p- 172.30.0.254` with
`nmap -6 -p- fd00:6:6::fe`, then
`curl 'http://[fd00:6:6::fe]:<port>/'`.

## Stage 6

The change log from stage 5 gives you the serials `00:00:10` to `00:00:1f`,
so only the vendor part is unknown. `grep -i raspberry
/usr/share/nmap/nmap-mac-prefixes` gives you the vendor prefixes. Build one
address per prefix by hand: `fd00:c::XXYY:ZZff:fe00:10` (XX = first byte with
bit 0x02 flipped, see the table in the README, e.g. `28` → `2a`). You don't
need a list for the serials: they are the last hex digit, so `/124` covers all
16. Put all prefixes into one command:
`nmap -6 -sn fd00:c::XXYY:ZZff:fe00:10/124 fd00:c::…/124 …`.
Then a quick TCP scan of the devices you found shows which one has a web
login (port 80): `nmap -6 <addresses>`. IoT devices often keep their factory
password: `http-brute`, then `curl -u user:password`.

## Stage 7

The login page mentions a telnet shell with the same account. Inside, a
plain `ping -6 ff02::1%eth0` only shows link-local addresses. Use your own
**global** address as source so the hosts answer with theirs:
`ping -6 -c2 -I <your global address> ff02::1%eth0`. Compare the list with
the hosts you already know. `fd00:c::ffff:ffff:ffff:fffe` is Docker's own
gateway (your laptop again), leave it out.

## Bonus

Scan the other three devices for TCP and UDP:
`nmap -6 -sS -sU -p T:1-1024,1883,U:5683 <addresses>`. Then run the matching
script on each device and read the whole output:

```bash
nmap -6 -p1883 --script mqtt-subscribe <address>
nmap -6 -sU -p5683 --script coap-resources <address>
nmap -6 -p502 --script modbus-discover <address>
```

CoAP needs two runs: the first lists the resources, the second fetches one
with `--script-args coap-resources.uri=/<resource>` (the path exactly as listed).
