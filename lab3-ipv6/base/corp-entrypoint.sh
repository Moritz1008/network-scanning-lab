#!/bin/sh
# Route the outside network (lab) through the CoolCorp router, then exec the
# service. Needs cap_add NET_ADMIN. Override with OUTSIDE_NET / CORP_ROUTER.
# NO_OUTSIDE_ROUTE=1 skips the route: the host then only talks to corp
# (used for the internal hosts of stage 7, which need a pivot).
OUTSIDE_NET="${OUTSIDE_NET:-fd00:6:6::/64}"
CORP_ROUTER="${CORP_ROUTER:-fd00:c::1}"

if [ "${NO_OUTSIDE_ROUTE:-0}" = "1" ]; then
  [ "$#" -eq 0 ] && set -- sleep infinity
  exec "$@"
fi

# The corp interface needs a moment until DAD is done; retry briefly.
i=0
until ip -6 route replace "$OUTSIDE_NET" via "$CORP_ROUTER" 2>/dev/null; do
  i=$((i + 1))
  if [ "$i" -ge 20 ]; then
    echo "[corp] WARNING: could not add route $OUTSIDE_NET via $CORP_ROUTER" >&2
    break
  fi
  sleep 0.5
done

[ "$#" -eq 0 ] && set -- sleep infinity
exec "$@"
