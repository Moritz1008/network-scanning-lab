# Linux CLI cheat sheet

The commands you need in the labs, for anyone who doesn't use a Linux shell
every day. Everything here works inside the attacker container
(`docker compose exec attacker bash`).

## Shell basics

| Keys / syntax | What it does |
| --- | --- |
| `Tab` | Complete a command or file name (press twice to list options) |
| `↑` / `↓` | Scroll through earlier commands |
| `Ctrl+C` | Stop the running command (a hanging `ping`, `nc`, scan, …) |
| `Ctrl+D` or `exit` | Leave the shell / the container |
| `Ctrl+L` or `clear` | Clear the screen |
| `cmd --help` | Short help for a command (there is no `man` in the container) |
| `cmd1 \| cmd2` | Pipe: feed the output of `cmd1` into `cmd2` |
| `cmd > file` | Save output to a file (overwrites); `>>` appends |
| `cmd 2>&1` | Also capture error messages (stderr) |
| `sudo` | Not needed: you are already `root` in the container |

## Files and directories

```bash
pwd                      # where am I?
ls -la                   # list files, including hidden ones, with details
cd /work                 # change directory (/work is shared with your host)
cd ..                    # one directory up
cat file.txt             # print a whole file
grep FLAG file.txt       # lines that contain FLAG
cp a b                   # copy; mv a b to move/rename; rm a to delete
mkdir notes              # create a directory
```


## Network: your own machine

```bash
ip a                     # interfaces and their IPv4/IPv6 addresses
ip route                 # IPv4 routing table
ip -6 route              # IPv6 routing table
ip -6 route add <network> via <gateway>   # add a route (lab 3)
ip -6 neigh              # IPv6 neighbours this host has seen (like arp -n)
```

## Network: reaching other hosts

```bash
ping -c 3 172.30.0.10           # IPv4, stop after 3 packets
ping -6 -c 3 fd00:6:6::10       # Same with IPv6
ping -6 ff02::1%eth0            # all IPv6 hosts on the link (Ctrl+C to stop)
traceroute -6 fd00:6:6::10      # which routers are on the way
dig example.lab AAAA @server    # DNS lookup (A for IPv4, AAAA for IPv6)
dig -x fd00:6:6::10 @server     # reverse lookup (address → name)
```

IPv6 addresses in URLs need square brackets: `http://[fd00:6:6::10]:8080/`.
Link-local addresses (`fe80::…`) need the interface: `fe80::1%eth0`.

## Talking to a service

```bash
nc 172.30.0.10 80               # open a raw TCP connection
nc -6 fd00:6:6::10 31337        # the same over IPv6
nc -u 172.30.0.10 161           # UDP instead of TCP
curl http://172.30.0.10/        # fetch a web page
curl -u user:pass http://…/     # with HTTP basic auth
telnet 172.30.0.10 23           # interactive Telnet login
ssh user@172.30.0.10            # SSH login
```

`nc` and `telnet` keep the connection open: press `Ctrl+C` to cancel(nc) or
`Ctrl+D` then type (telnet) to exit.

## nmap in one minute

```bash
nmap -sn 172.30.0.0/24          # which hosts are up (no port scan)
nmap 172.30.0.10                # top 1000 TCP ports
nmap -p- 172.30.0.10            # all 65535 TCP ports
nmap -p 80,443 -sV 172.30.0.10  # specific ports, detect service versions
nmap -sU -p 161 172.30.0.10     # UDP port
nmap -6 fd00:6:6::10            # IPv6 target
nmap --script <name> -p … host  # run an NSE script
nmap -oN /work/scan.txt …       # save results to a file
```
