#!/bin/sh
# CoolCtl 3000: telnet maintenance login (same default account as the web
# interface) via inetd, then the web interface in the foreground.
cat > /etc/inetd.conf <<'CONF'
telnet stream tcp6 nowait root /usr/sbin/telnetd telnetd
CONF
/usr/sbin/inetd
exec python3 /opt/iot/coolctl_web.py
