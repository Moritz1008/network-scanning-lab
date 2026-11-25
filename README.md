# Network Scanning Lab

Docker environment for the hands-on parts of the "Network Scanning" session
(Practical IT Security). Everything runs in an isolated Docker network on
your own machine; nothing is sent to the university network or the Internet.

## Requirements

Bring a laptop with the following. Set it up **before the session**: the
build downloads images and packages, this may take a while.

| What | Details |
| --- | --- |
| Docker | Windows/macOS: [Docker Desktop](https://docs.docker.com/desktop/), current version. Linux: Docker Engine **28 or newer** (lab 3 needs it). Check with `docker version`. |
| Docker Compose | Plugin version (`docker compose`, not the old `docker-compose`). Included in Docker Desktop; on Linux install `docker-compose-plugin`. Check with `docker compose version`. |
| Windows only | WSL 2 backend for Docker Desktop (the default) and virtualization enabled in the BIOS/UEFI. |
| Linux only | Your user can run Docker without `sudo` (member of the `docker` group), or you use `sudo docker …`. |
| Git | To clone the repo (or download it as a ZIP). |
| Wireshark | For lab 1, installed on your **host**. Windows: keep the Npcap option "support loopback traffic capture" ticked during install. Linux: your user needs capture rights (group `wireshark`) or run it with `sudo`. |
| Disk space | About 3 GB free (images about 1.5 GB plus build cache). |
| RAM | 8 GB in the laptop is enough; Docker Desktop's default memory setting works. |
| Shodan.io Account | Needed for Lab 2. You can sign up here: https://www.shodan.io/ |

Nothing else is needed: all scanners and clients run inside the attacker
container.

**Check your setup** (with Internet, before the session):

```bash
docker version                  # Linux: Server version 28 or newer
docker compose version
git clone <repo-url>
cd network-scanning-lab
docker compose build
docker compose --profile lab3 up -d
docker compose --profile "*" down
```

If all commands finish without errors, you are ready.

## Quick start
Execute this in a terminal inside of this directory

```bash
docker compose build            # do this before the session
docker compose up -d
docker compose exec attacker bash
```

You are now in the attacker container. All scans start from here.

New to the Linux shell? The [Linux CLI cheat sheet](CHEATSHEET.md) has the
commands you need (`ls`, `cat`, `ip a`, `nc`, `curl`, `vi`, …).

## Labs

Each lab has its own targets, started with a profile:

| Lab | Topic | Start |
| --- | --- | --- |
| 1 | Fundamentals (nmap, Wireshark) ([task](lab1/README.md)) | `docker compose --profile lab1 up -d` |
| 2 | Internet-scale scanning (ZMap, Shodan) | `docker compose --profile lab2 up -d` |
| 3 | IPv6 and IoT (nmap)([task](lab3-ipv6/README.md)) | `docker compose --profile lab3 up -d` |

Stop everything:

```bash
docker compose --profile "*" down
```

## What is in the attacker container

| Purpose | Tools |
| --- | --- |
| Scanning | `nmap` (with NSE scripts), `ncat`, `ndiff`, `zmap` |
| Packet capture | `tshark`, `tcpdump` |
| IPv6 | `ndisc6`, THC-IPv6 toolkit (`atk6-*`), IPv6 toolkit (`scan6`), `traceroute` |
| IoT | `mosquitto_sub`/`mosquitto_pub` (MQTT), `coap-client-notls` (CoAP), `mbpoll` and Python `pymodbus` (Modbus) |
| Logins | `telnet`, `ssh` |
| Other | `curl`, `jq`, `dig`, `nc`, `ip`, `ping`, `vim` |

The folder `work/` is shared with the container as `/work`. Save captures
there (`tcpdump -w /work/scan.pcap`) and open them in Wireshark on your host.

## Network

| | Range |
| --- | --- |
| IPv4 | `172.30.0.0/24` |
| IPv6 | `fd00:6:6::/64` |
| Lab 3 only | second network `corp`: internal, IPv6 only, behind the lab 3 router (its prefix is part of the lab) |

## Rules

Scan only this lab network. Scanning systems without permission can be a
criminal offence.

## Troubleshooting

- **IPv6 does not work (older Docker):** add `{"ipv6": true, "fixed-cidr-v6": "fd00:dead:beef::/64"}`
  to `/etc/docker/daemon.json` and restart Docker.
- **Subnet conflict:** change the `subnet` lines in `compose.yaml`.
- **Lab 3, corp unreachable:** the route you added in stage 1 is lost when the
  attacker container restarts. Add it again (see the lab 3 task).
- **Reset:** `docker compose --profile "*" down && docker compose up -d`
