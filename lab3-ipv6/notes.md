stage 1
nmap hat aber ohne zone index funktioniert
zone index bei nc nötig!

# stage 3
kandidaten-datei erstellen dauert ewig und fordert shell-scripting statt nmap-skills. -> candidates file zur Verfügung stellen!

`targets-ipv6-wordlist`

`targets-ipv6-map4to6`

`nmap -6 -sn --min-hostgroup 1024 --script targets-ipv6-wordlist --script-args 'newtargets,targets-ipv6-subnet={fd00:c::/64}'`

vielleicht nen hinweis für den curl für stage 4


danach:

`docker compose --profile lab3 up -d --remove-orphans`

# stage 4
for i in $(seq 0 255); do printf 'fd00:c::%x\n' $((0x1000 + i)); done > s4-candidates-dhcp.txt

# stage 5
`atk6-dnsrevenum6 fd00:6:6::53 fd00:c::/64`
nmap -6 -p- fd00:c::7a3e:91b2:4c5d:e816
nc fd00:c::7a3e:91b2:4c5d:e816 873


# stage 6
