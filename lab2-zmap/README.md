# Lab 2: Northstar CTF - The Missing Handover

You are part of Northstar's security team. After a routine maintenance window,
the operations team can no longer access its technical handover. The change
records are incomplete, and the last service inventory, dated 1 November 2026,
still lists three HTTP services on port 80. Nobody knows how much of it is
still accurate.

Your team has been given a workstation inside Northstar's lab network and
ZMap to rediscover the services. An archived copy of the inventory is available
at `/opt/lab2/snapshot.json`. The surviving services hold fragments of the
missing handover: some are easy to overlook, others are not where their labels
suggest they should be.

Find the services, follow their clues, and recover all three flags in the
format `FLAG{...}`. Reaching the final flag will require combining what you
learn along the way to unlock the handover.

Your authorised scope is `172.30.0.0/24`, TCP ports `80` and `8080`, with a
maximum scan rate of `50 packets/s`.

## Start

Run these commands on your machine, from the project directory:

```bash
docker compose --profile lab2 up -d --build --wait
docker compose exec attacker bash
```

Everything else happens in the attacker shell. Keep your results in
`/work/lab2`, which is `work/lab2` on your machine:

```bash
mkdir -p /work/lab2
```

## Stage 0: Planning the Scan

Before you type a ZMap command, answer the planning questions from the
lecture. Every option in your command should answer one of them.

| Question                                   | Your decision | ZMap option                         |
| ------------------------------------------ | ------------- | ----------------------------------- |
| Which addresses are we allowed to probe?   |               | target range                        |
| What do we want to detect?                 |               | `-M` (probe module)                 |
| Which destination ports matter?            |               | `-p`                                |
| How much traffic may we generate?          |               | `-r`                                |
| Could local exclusions remove our targets? |               | `-b`                                |
| What results do we need afterwards?        |               | `-O`, `-f`, `--output-filter`, `-o` |
| How long should we accept late replies?    |               | `-c`                                |

Then fill in the template:

```bash
zmap <range> -M <probe module> -p <port> -r <rate> \
  -b <exclusion file> -c <seconds> \
  -O csv -f saddr,sport,classification \
  --output-filter='success = 1 && repeat = 0' \
  -o /work/lab2/port-<port>.csv
```

Hints:

- `zmap --help`, `zmap --list-probe-modules` and
  `zmap -M tcp_synscan --list-output-fields` explain the options.
- The installed ZMap 2.1.1 scans one port per run.
- ZMap's default send rate is far above 50 packets/s.
- ZMap's default exclusions are in `/etc/zmap/blacklist.conf`. Is our range
  listed there?
- If ZMap cannot detect the gateway's MAC address, run `ping -c 1 172.30.0.1`
  once and try again. `172.30.0.1` is the Docker host, your next hop.
  [Under the Hood](#under-the-hood) asks why this is needed.

## Stage 1: The Missing Note

Rediscover Northstar's services with ZMap and locate the portal. Recover the
first flag and the maintenance note left behind by the operations team.
The note points you towards the gateway and the next piece of the handover.

Record your port-80 scan so you can look under the hood afterwards. Start the
capture, run your planned scan, then stop the capture:

```bash
tcpdump -n -i eth0 -w /work/lab2/zmap-80.pcap 'tcp port 80' &
sleep 1
# your port-80 scan from Stage 0
kill %1
```

## Under the Hood

The capture shows what ZMap actually sent. Answer these questions before you
move on; they are part of the debrief. You can also open the capture in
Wireshark on your machine (`work/lab2/zmap-80.pcap`).

1. **Random order** (lecture: _Random order without a list_). Are the probes
   sent in address order?

   ```bash
   tcpdump -n -r /work/lab2/zmap-80.pcap 'tcp[tcpflags] == tcp-syn' | head -20
   ```

   A dry run prints the probes instead of sending them. Run this twice: is
   the order the same? What happens without `--seed`? (`-T 1` uses a single
   send thread.)

   ```bash
   zmap --dryrun -T 1 --seed 7 172.30.0.0/24 -p 80 -b /dev/null -r 50 \
     2>/dev/null | grep daddr | head -5
   ```

2. **One probe per target** (lecture: _Stateful vs. stateless_). How many
   probes did ZMap send (see its last status line)? Was any probe
   retransmitted? Your capture holds one SYN more than that: which address
   appears twice? Question 3 explains why.

   ```bash
   tcpdump -n -r /work/lab2/zmap-80.pcap 'tcp[tcpflags] == tcp-syn' | wc -l
   tcpdump -n -r /work/lab2/zmap-80.pcap 'tcp[tcpflags] == tcp-syn' \
     | awk '{print $5}' | sort | uniq -d
   ```

3. **Raw Ethernet frames** (lecture: _Stateful vs. stateless_). Which
   destination MAC address do the probes use? Compare it with `ip neigh`.
   Why does every probe go to the same MAC address, even for targets in your
   own subnet? Why did ZMap need the ping to `172.30.0.1`?

   ```bash
   tcpdump -n -e -r /work/lab2/zmap-80.pcap 'tcp[tcpflags] == tcp-syn' | head -5
   ```

4. **Replies prove themselves** (lecture: _Replies prove themselves_). List
   every packet exchanged with the portal (`-S` prints absolute sequence
   numbers). How does the SYN/ACK's acknowledgement number relate to the
   probe's sequence number? Do the probes to different targets use the same
   source port? Which packet follows the SYN/ACK, and who sent it: ZMap or the
   kernel?

   ```bash
   tcpdump -n -S -r /work/lab2/zmap-80.pcap host 172.30.0.10
   ```

   On that slide, "MAC" means message authentication code, not MAC address.

5. **Scale** (lecture: _ZMap: the idea in one picture_). ZMap's status lines
   show the elapsed time and send rate. How long did one port take? At that
   rate, how long would all 2^32 IPv4 addresses take? What send rate does the
   44-minute scan from the lecture need?

## Stage 2: The Mislabelled Gateway

Find out what the gateway actually reveals, even if its response does not
match the old inventory. Recover the second flag and the missing access clue.
Your next destination is the status service, wherever it is running now.

## Stage 3: The Locked Handover

Locate the current status service and combine the clues from the portal and
gateway to unlock its handover. Recover the final flag to complete the mission.

The inventory still lists the status service on port 80, but your scan files
only contain successful replies. Run your port-80 scan once more with
`--output-filter='success = 0 && repeat = 0'` and a new output file, for
example `/work/lab2/port-80-closed.csv`. Which addresses answered port 80 with
a reset, and which did not answer at all? What does that say about the
inventory entry?

## Debrief

Be ready to discuss:

- ZMap reported an open port 80 on the gateway. What did that prove, and what
  did it not? Which tool from the ZMap ecosystem automates what you did with
  `curl` and `nc`? (lecture: _Open port ≠ service_)
- For each entry in `/opt/lab2/snapshot.json`: still accurate, different
  protocol, or moved? Which result shows it? (lecture: _Limits and the legal
  line_)

## If Something Looks Wrong

- **"no addresses are eligible to be scanned":** check the exclusions from
  Stage 0.
- **An open port on `172.30.0.1`:** that is the Docker host, your own
  machine. Another container on your machine publishes port 80 or 8080.
  Ignore the hit or stop that container. A reset from `172.30.0.1` in
  Stage 3 is normal.
- **More than three hits:** Lab 3's targets also serve port 80. Stop them with
  `docker compose stop v6-target v6-decoy v6-fridge` on your machine.
