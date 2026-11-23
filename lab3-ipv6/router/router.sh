#!/bin/sh
# CoolCorp HQ edge router. Forwarding is switched on via compose sysctls.
set -e

# IPv6: forward unicast between lab and corp, never multicast.
# (Link-local multicast like ff02::1 is never routed anyway; this rule makes
# sure no wider-scoped multicast crosses either.)
ip6tables -P FORWARD ACCEPT
ip6tables -A FORWARD -d ff00::/8 -j DROP
ip6tables -A FORWARD -s ff00::/8 -j DROP

# IPv4: the corp network is IPv6-only; never forward IPv4 at all.
iptables -P FORWARD DROP

# Stage 6 - dual-stack gap: the admin interface is firewalled on IPv4 ...
iptables -A INPUT -p tcp --dport 8080 -j DROP
# ... and the matching ip6tables rule was "forgotten". (Do not add it.)
# Only the corp-facing address is closed, so stage 6 is solved from the
# outside (fd00:6:6::fe vs 172.30.0.254) and not by accident in stage 3.
ip6tables -A INPUT -d fd00:c::1 -p tcp --dport 8080 -j DROP

# Admin page, generated from FLAG6 so the flag stays in compose.yaml.
mkdir -p /srv/admin
cat > /srv/admin/index.html <<HTML
<!DOCTYPE html>
<html>
  <head><meta charset="utf-8"><title>coolcorp-edge - router admin</title></head>
  <body>
    <!-- Fictional router for a training lab. -->
    <h1>coolcorp-edge :: admin</h1>
    <p>Firewall: IPv4 rules active. IPv6 rules: <i>todo</i></p>
    <p><b>STAGE 6 FLAG: ${FLAG6}</b></p>
    <h2>Change log</h2>
    <ul>
      <li>2026-11-03 admin interface blocked from outside (iptables)</li>
      <li>2026-11-10 new IoT batch online in corp: 16 Raspberry Pi based
          sensors, NIC serials 00:00:10 to 00:00:1f (vendor part of the MAC
          is the Raspberry Pi one). They configure their addresses
          themselves (SLAAC, EUI-64), so they are not in DNS.</li>
    </ul>
  </body>
</html>
HTML

echo "[router] up: lab <-> corp IPv6 unicast forwarding, multicast and IPv4 blocked"
echo "[router] admin interface on :8080 (dual-stack socket, IPv4 firewalled)"
cd /srv/admin
exec python3 -m http.server 8080 --bind ::
