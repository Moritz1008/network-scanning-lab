# CoolCorp HQ edge router (lab 3): connects the outside network (lab) with the
# internal corp network. Forwards IPv6 unicast, never multicast, never IPv4.
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      iproute2 iptables python3 \
    && rm -rf /var/lib/apt/lists/*

COPY router.sh /usr/local/bin/router.sh
RUN chmod 755 /usr/local/bin/router.sh

CMD ["/usr/local/bin/router.sh"]
