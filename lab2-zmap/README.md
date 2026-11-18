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

## Stage 1: The Missing Note

Rediscover Northstar's services with ZMap and locate the portal. Recover the
first flag and the maintenance note left behind by the operations team.
The note points you towards the gateway and the next piece of the handover.

## Stage 2: The Mislabelled Gateway

Find out what the gateway actually reveals, even if its response does not
match the old inventory. Recover the second flag and the missing access clue.
Your next destination is the status service, wherever it is running now.

## Stage 3: The Locked Handover

Locate the current status service and combine the clues from the portal and
gateway to unlock its handover. Recover the final flag to complete the mission.
