# Lab 3: Find me if you can (IPv6 edition)

One host in the lab network listens only on IPv6, on an unusual port, and
its address cannot be guessed. Find it and fetch the flag.

## Start

```bash
docker compose --profile lab3 up -d --build
docker compose exec attacker bash
```

## Task

1. Find every host on the link. Hint: `ff02::1`
2. Scan them with `nmap -6`. One port does not belong there.
3. Fetch the flag: `nc -6 <address> <port>`

Rules: scan only the lab network, no flooding (`-T5`, `ipv6-ra-flood`).

Bonus:

- Scan the same host via IPv4. What is different?
- Which host looks like a fridge controller?

The solution is not in this repository on purpose.
