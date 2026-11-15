# Network Scanning Lab

Docker environment for the hands-on parts of the "Network Scanning" session
(Practical IT Security). Everything runs in an isolated Docker network on
your own machine; nothing is sent to the university network or the Internet.

## Requirements

- Docker with the Compose plugin (Docker Desktop on Windows/macOS, Docker Engine on Linux)
- About 1 GB of disk space

## Quick start

```bash
git clone <repo-url>
cd network-scanning-lab
docker compose build            # do this before the session
docker compose up -d
docker compose exec attacker bash
```

You are now in the attacker container. All scans start from here.

## Labs

Each lab has its own targets, started with a profile:

| Lab | Topic | Start |
| --- | --- | --- |
| 1 | Fundamentals (nmap, Wireshark) | `docker compose --profile lab1 up -d` |
| 2 | Internet-scale scanning (ZMap, Shodan) | `docker compose --profile lab2 up -d` |
| 3 | IPv6 ([task](lab3-ipv6/README.md)) | `docker compose --profile lab3 up -d` |

Stop everything:

```bash
docker compose --profile "*" down
```

## What is in the attacker container

| Purpose | Tools |
| --- | --- |
| Scanning | `nmap` (with NSE scripts), `ncat`, `ndiff`, `zmap` |
| Packet capture | `tshark`, `tcpdump` |
| IPv6 | `ndisc6`, THC-IPv6 toolkit (`atk6-*`) |
| Other | `curl`, `jq`, `dig`, `nc`, `ip`, `ping`, `vim` |

The folder `work/` is shared with the container as `/work`. Save captures
there (`tcpdump -w /work/scan.pcap`) and open them in Wireshark on your host.

## Network

| | Range |
| --- | --- |
| IPv4 | `172.30.0.0/24` |
| IPv6 | `fd00:6:6::/64` |

## Rules

Scan only this lab network. Scanning systems without permission can be a
criminal offence.

## Troubleshooting

- **IPv6 does not work (older Docker):** add `{"ipv6": true, "fixed-cidr-v6": "fd00:dead:beef::/64"}`
  to `/etc/docker/daemon.json` and restart Docker.
- **Subnet conflict:** change the two `subnet` lines in `compose.yml`.
- **Reset:** `docker compose --profile "*" down && docker compose up -d`
