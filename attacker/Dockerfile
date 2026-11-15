# Shared attacker container for all three labs.
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
      # lab 1: scanning and packet analysis
      nmap ncat ndiff tshark tcpdump \
      # lab 2: internet-scale scanning, Shodan lookups
      zmap curl ca-certificates jq dnsutils \
      # lab 3: IPv6
      ndisc6 thc-ipv6 \
      # basics
      iproute2 iputils-ping netcat-openbsd vim-tiny less \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work
CMD ["bash"]
