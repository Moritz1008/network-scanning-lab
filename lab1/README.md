# Lab 1 — CoolCorp Cold-Storage Incident (Scanning Fundamentals)

> **Scenario.** At the cold-chain logistics company **CoolCorp**, refrigeration controllers have been hijacked. The incident-response team already has a foot in the door: a Linux host inside the CoolCorp network — your `attacker` container. Your job: map the network, find the compromised devices, and trace the attacker's path all the way to the controller.

Four stages, from **passive capture** to an **idle scan**. Each stage gives you a `FLAG{...}`. **That flag is at the same time the token for the next stage** — without the previous one you can't move on.

---

## Start

```bash
docker compose --profile lab1 up -d --build
docker compose exec attacker bash
```

You are now in the `attacker` container. All scans run from here.

- Lab network: `172.30.0.0/24`

---

## Stage 1 — The Beacon

A hijacked **thermostat** is running an implant. It periodically beacons telemetry out — including to **your own machine**. Wireshark is passive: it only listens, it sends nothing. That's exactly how you catch the broadcast.

**Goal:** Capture the beacon packet and read the maintenance token (`FLAG{...}`) from the clear-text payload.

**How to — Option A (on your own machine, the way a technician would):**
1. Start **Wireshark** on your host.
2. Pick the right interface:
   - **Windows:** `Adapter for loopback traffic capture`
   - **macOS:** `lo0`
   - **Linux:** the Docker bridge interface (`docker0` or `br-…`)
3. Open the right packet → the payload contains
   `maint-token=FLAG{...}`

   Important the flag might have some empty spaces. These are not meant to be! Remove them!

## Stage 2 — Host Discovery

You have a token, but no map of the network yet. Get an overview:
**Which hosts are alive in the `/24`?**

CoolCtl's **maintenance jump host** is listening somewhere on the network on **TCP 2323**. Find the right host, connect, and authenticate with your Stage 1 token.

Hints:
- Discover the host
- You can find the service with a targeted port scan across the live hosts.
- Connect to the host and enter the token:
  ```bash
  ncat <ip> 2323
  ```

➡️ With the correct token the service hands you the **Stage 2 flag** and the
mission for Stage 3.

---

## Stage 3 — Ports & Versions

The maintenance host can do more than you've seen so far. Find **all** open ports, track down the hidden **CoolCtl console**, and determine its **version** — the service gives itself away through its banner.

Hints:
- The port wasn't open before (maybe check what you found in Stage 2)
- Then connect as in Stage 2 and authenticate with the **Stage 2 flag**.

➡️ You get the **Stage 3 flag** and a situation report on the actual target:
the controller `coolctl-core`.

---

## Stage 4 — The Printer Pivot

The controller **`coolctl-core`** is walled off by a firewall: a direct scan from you only shows `filtered` — you see nothing. **But** the controller **trusts the old network printer `coolcorp-printer`** (JetDirect).

Turn it around: use the printer as a **zombie** for an **idle scan**. The printer has a predictable IP ID — with it you can scan *blindly* through it, without ever sending a single packet to the controller yourself.

Hints:
- Compare for yourself first: a direct scan vs. what you see through the zombie.
  ```bash
  nmap -sI {zombie} {target} -p {ports}
  ```

- Report the **open port** to the IR team on the maintenance host, **port 9000**,
  in the format `FLAG3:<port>`:
  ```bash
  ncat <maint-ip> 9000
  ```

➡️ If both token **and** port are correct, you get the **final flag**. That
completes Part I.

---

## Stop / Reset

```bash
docker compose --profile lab1 down
docker compose --profile lab1 up -d          # fresh start
```
