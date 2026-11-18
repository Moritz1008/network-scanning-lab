# Lab 2: Northstar CTF - Solution

Instructor walkthrough with spoilers. Give students only the [scenario](README.md).
The steps below follow its three stages and show the commands, expected findings,
and clues leading to the next stage.

## Preparation

Run these commands **on the host**, from the project directory. Docker must
use Linux containers; stop targets from other lab profiles before starting.

```text
docker compose --profile lab2 up -d --build --wait
```

If an earlier version of the lab is already running, refresh its targets
so nginx loads the current configuration:

```text
docker compose --profile lab2 up -d --force-recreate --wait zmap-portal zmap-banner zmap-status
```

Open the attacker shell:

```text
docker compose exec attacker bash
```

**Run all remaining commands in the attacker container's Bash shell.**

## Stage 1: The Missing Note

Discover the current endpoints before relying on the archived inventory.
The installed ZMap 2.1.1 scans one target port per run:

```bash
mkdir -p /work/lab2
ping -c 1 -W 1 172.30.0.1

for PORT in 80 8080; do
  zmap 172.30.0.0/24 -p "$PORT" -M tcp_synscan \
    -i eth0 -b /dev/null -r 50 -c 3 -T 1 \
    -O csv -f saddr,sport,classification \
    --output-filter='success = 1 && repeat = 0' \
    -o "/work/lab2/port-$PORT.csv"
done

cat /work/lab2/port-80.csv /work/lab2/port-8080.csv
```

`-b /dev/null` disables the default exclusions for this explicitly selected
lab subnet. `-r 50` limits the send rate; `-c 3` allows three seconds for late
responses. The output filter keeps successful, non-duplicate responses.

Expected hits, in any order:

| Port | Addresses |
| --- | --- |
| 80 | `172.30.0.10`, `172.30.0.20` |
| 8080 | `172.30.0.30` |

Probe the first port-80 candidate with HTTP:

```bash
curl --noproxy '*' --connect-timeout 1 --max-time 3 -i \
  http://172.30.0.10/
```

The response is HTTP 200 with the title **Northstar Portal**. Read the raw
HTML: its comment contains the first flag and the maintenance note.

```text
FLAG{read_beyond_the_page}
Maintenance note: The current status service keeps its handover at /handover.
Required HTTP header: X-Northstar-Key
The gateway banner provides the value.
```

**Next:** Find the gateway. Keep the path and header name; the header value
is still missing.

## Stage 2: The Mislabelled Gateway

Try HTTP on the other port-80 candidate:

```bash
curl --noproxy '*' --connect-timeout 1 --max-time 3 -i \
  http://172.30.0.20/
```

This request fails, for example with an HTTP/0.9 error or a connection reset.
The open port does not guarantee HTTP. Read the service's greeting directly:

```bash
timeout 3 nc -w 2 172.30.0.20 80 </dev/null
```

Expected banner:

```text
SSH-2.0-LabSSH_1.0
FLAG{a_port_is_not_a_protocol}
Maintenance handover key: northstar-maintenance-42
```

This supplies the second flag and the missing header value. The service is
a banner emulator, so an SSH login is not part of the solution.

**Next:** Locate the status service using the remaining discovery result.
Combine the gateway's key with the portal's maintenance note.

## Stage 3: The Locked Handover

Inspect the endpoint discovered on port 8080:

```bash
curl --noproxy '*' --connect-timeout 1 --max-time 3 -i \
  http://172.30.0.30:8080/
```

HTTP 200 and the title **Northstar Status** identify the service. Its landing
page says the handover is locked. Follow the path found in the portal:

```bash
curl --noproxy '*' --connect-timeout 1 --max-time 3 -i \
  http://172.30.0.30:8080/handover
```

Expect **HTTP 403 Forbidden**. The path is correct, but the key is missing.
Repeat the request with the header name from Stage 1 and its value from Stage 2:

```bash
curl --noproxy '*' --connect-timeout 1 --max-time 3 -i \
  -H 'X-Northstar-Key: northstar-maintenance-42' \
  http://172.30.0.30:8080/handover
```

The response is **HTTP 200 OK**, with this body:

```text
FLAG{open_port_is_not_a_service}
```

All three flags have been recovered. The handover is unlocked and the mission
is complete.

## How the Archived Inventory Fits

To inspect the historical entries:

```bash
jq -r '.matches[] | [.ip_str, .port, .http.title] | @tsv' \
  /opt/lab2/snapshot.json
```

It lists the portal, gateway and status service on port 80. The portal still
matches; the gateway now returns a different protocol's greeting. The old
status endpoint at `172.30.0.30:80` is absent from the successful scan results,
while the current HTTP service is found at `172.30.0.30:8080`.

## Instructor Check

The existing preflight verifies the scan results, all three flags, and the
handover with missing, incorrect and correct keys:

```bash
bash /opt/lab2/check-lab.sh
```

Expected final line:

```text
PASS: expected ZMap hits, three CTF flags, handover gate and snapshot verified.
```

If discovery fails, check the lab gateway and Docker forwarding. A 404 at the
handover usually means an incorrect path or stale nginx configuration; use
exactly `/handover`, without a trailing slash, and refresh the targets if needed.

## Alternative Scanner Check

The current lab does **not** enforce exclusive use of ZMap. Checks against
the three lab targets on ports 80 and 8080 produced these results:

| Method | Observed result |
| --- | --- |
| Nmap SYN scan (`-sS`) | Found the same three open endpoints. |
| Nmap TCP connect scan (`-sT`) | Found the same three open endpoints. |
| Nmap service detection (`-sT -sV --version-light`) | Identified HTTP on the portal and status endpoints, and an SSH-style greeting on the gateway. |
| Netcat port checks (`-zv`) | Connected to all three open endpoints; the other three IP:port combinations refused connections. |

For example, run either Nmap scan inside the attacker container:

```bash
nmap -n -Pn -sS -p 80,8080 --max-rate 50 --max-retries 1 --reason \
  172.30.0.10 172.30.0.20 172.30.0.30

nmap -n -Pn -sT -p 80,8080 --max-rate 50 --max-retries 1 --reason \
  172.30.0.10 172.30.0.20 172.30.0.30
```

A target cannot reliably infer the originating tool from a TCP SYN. Connect
scans also use the same connection setup as the HTTP and banner requests
needed to solve the CTF. Removing Nmap would therefore leave other discovery
methods available and would affect the shared tools used by other labs.

Reliable tool restrictions would require a separate, controlled Lab 2
execution environment rather than the current root shell with raw-socket and
network-administration capabilities. ZMap is currently an exercise requirement,
not a technical access restriction.
