# Base image for every host in the corp network (lab 3).
# The entrypoint adds the route back to the outside network via the
# CoolCorp router, then runs the service given as command.
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      iproute2 python3 \
    && rm -rf /var/lib/apt/lists/*

COPY corp-entrypoint.sh /usr/local/bin/corp-entrypoint.sh
COPY banner.py /usr/local/bin/banner
# Strip CR in case the files were checked out with Windows line endings.
RUN sed -i 's/\r$//' /usr/local/bin/corp-entrypoint.sh /usr/local/bin/banner \
    && chmod 755 /usr/local/bin/corp-entrypoint.sh /usr/local/bin/banner

ENTRYPOINT ["/usr/local/bin/corp-entrypoint.sh"]
