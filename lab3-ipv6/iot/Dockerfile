# IoT devices of CoolCorp HQ (lab 3, stages 6 and 7). One image for all four
# devices; the compose command picks the service. Build context: lab3-ipv6/
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      iproute2 python3 \
      mosquitto mosquitto-clients \
      openbsd-inetd inetutils-telnetd \
      iputils-ping netcat-openbsd \
      vim-tiny \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/vim.tiny /usr/local/bin/vim

COPY base/corp-entrypoint.sh /usr/local/bin/corp-entrypoint.sh
COPY iot/coap_server.py /opt/iot/coap_server.py
COPY iot/modbus_server.py /opt/iot/modbus_server.py
COPY iot/coolctl_web.py /opt/iot/coolctl_web.py
COPY iot/start-mqtt.sh iot/start-coolctl.sh /opt/iot/
COPY iot/mosquitto.conf /etc/mosquitto/conf.d/lab.conf
COPY fridge/index.html /opt/iot/index.html
# Strip CR in case the files were checked out with Windows line endings.
RUN sed -i 's/\r$//' /usr/local/bin/corp-entrypoint.sh /opt/iot/*.sh /opt/iot/*.py \
      /etc/mosquitto/conf.d/lab.conf \
    && chmod 755 /usr/local/bin/corp-entrypoint.sh /opt/iot/*.sh

ENTRYPOINT ["/usr/local/bin/corp-entrypoint.sh"]

# Default account of the CoolCtl 3000 (web + telnet): admin / admin
RUN useradd -m -s /bin/bash admin && echo 'admin:admin' | chpasswd \
    && printf 'CoolCtl 3000 maintenance shell (fw 3.0.4)\nInternal controllers on this segment are not listed in DNS.\n' > /etc/motd
