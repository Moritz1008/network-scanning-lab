# Shared attacker container for all three labs.
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

# Fetch packages over HTTPS. Some networks (e.g. FortiGate antivirus) inspect
# plain-HTTP downloads and block the zmap .deb as malware with a 403.
# ca-certificates itself has to come over HTTP since the slim image lacks it.
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
    && sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/debian.sources \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
      # lab 1: scanning and packet analysis
      nmap ncat ndiff tshark tcpdump \
      # lab 2: internet-scale scanning, Shodan lookups
      zmap curl ca-certificates jq dnsutils \
      # lab 3: IPv6
      ndisc6 thc-ipv6 ipv6toolkit traceroute \
      # lab 3: IoT protocols and logins
      mosquitto-clients libcoap3-bin python3-pymodbus python3-serial-asyncio mbpoll \
      telnet openssh-client \
      # basics
      iproute2 iputils-ping netcat-openbsd vim-tiny less \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work
CMD ["bash"]
