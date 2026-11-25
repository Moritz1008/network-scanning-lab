FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      socat iptables python3 python3-scapy iproute2 tcpdump \
      nginx-light apache2-utils \
    && rm -rf /var/lib/apt/lists/*

COPY printer_zombie.py /opt/printer_zombie.py
WORKDIR /opt
