# CoolCorp HQ DNS server (lab 3, stage 5): authoritative for corp.lab and
# the reverse zone of fd00:c::/64.
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends nsd \
    && rm -rf /var/lib/apt/lists/*

COPY nsd.conf /etc/nsd/nsd.conf
COPY zones/ /etc/nsd/zones/
RUN nsd-checkconf /etc/nsd/nsd.conf \
    && nsd-checkzone corp.lab /etc/nsd/zones/corp.lab.zone \
    && nsd-checkzone 0.0.0.0.0.0.0.0.c.0.0.0.0.0.d.f.ip6.arpa /etc/nsd/zones/fd00-c.rev.zone

CMD ["nsd", "-d", "-c", "/etc/nsd/nsd.conf"]
