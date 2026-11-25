#!/usr/bin/env bash
# Instructor preflight. Reveals the expected targets and all flags, so it is
# not mounted into the attacker. Run from the project directory on the host:
#   docker compose cp lab2-zmap/material/check-lab.sh attacker:/tmp/check-lab.sh
#   docker compose exec attacker bash /tmp/check-lab.sh
set -euo pipefail

check_dir=$(mktemp -d /tmp/lab2-check.XXXXXX)
printf 'Preflight output: %s\n' "$check_dir"
printf 'Only scan scope: 172.30.0.0/24, TCP 80/8080, 50 packets/s.\n'
zmap --version

if ! ping -c 1 -W 1 172.30.0.1 >"$check_dir/gateway.log" 2>&1; then
  printf 'Cannot reach the lab gateway. Check Docker networking.\n' >&2
  exit 1
fi

for port in 80 8080; do
  zmap 172.30.0.0/24 -p "$port" -M tcp_synscan \
    -i eth0 -b /dev/null -r 50 -c 3 -T 1 \
    -O csv -f saddr,sport,classification \
    --output-filter='success = 1 && repeat = 0' \
    -o "$check_dir/port-$port.csv"
  awk -F, '$1 ~ /^172[.]30[.]0[.][0-9]+$/ {print $1 ":" $2}' \
    "$check_dir/port-$port.csv" | LC_ALL=C sort -u >"$check_dir/actual-$port.txt"
done

printf '172.30.0.10:80\n172.30.0.20:80\n' >"$check_dir/expected-80.txt"
printf '172.30.0.30:8080\n' >"$check_dir/expected-8080.txt"
for port in 80 8080; do
  if ! diff -u "$check_dir/expected-$port.txt" "$check_dir/actual-$port.txt"; then
    printf 'Unexpected ZMap hits on port %s. Check other profiles and forwarding.\n' "$port" >&2
    exit 1
  fi
done

curl --noproxy '*' --fail --silent --show-error --connect-timeout 1 --max-time 3 \
  http://172.30.0.10/ >"$check_dir/portal.html"
grep -q '<title>Northstar Portal</title>' "$check_dir/portal.html"
grep -Fq 'FLAG{read_beyond_the_page}' "$check_dir/portal.html"
grep -Fq '/handover' "$check_dir/portal.html"
grep -Fq 'X-Northstar-Key' "$check_dir/portal.html"
grep -Fq 'gateway banner' "$check_dir/portal.html"

curl --noproxy '*' --fail --silent --show-error --connect-timeout 1 --max-time 3 \
  http://172.30.0.30:8080/ >"$check_dir/status.html"
grep -q '<title>Northstar Status</title>' "$check_dir/status.html"
if grep -Fq 'FLAG{' "$check_dir/status.html"; then
  printf 'Status landing page must not disclose a flag.\n' >&2
  exit 1
fi

if ! timeout 3 nc -w 2 172.30.0.20 80 </dev/null >"$check_dir/banner.txt"; then
  printf 'Banner connection failed or timed out.\n' >&2
  exit 1
fi
grep -q '^SSH-2.0-LabSSH_1.0' "$check_dir/banner.txt"
grep -Fq 'FLAG{a_port_is_not_a_protocol}' "$check_dir/banner.txt"
grep -Fxq 'Maintenance handover key: northstar-maintenance-42' "$check_dir/banner.txt"

# Missing and incorrect keys must both keep the final flag locked.
for key_case in missing incorrect; do
  header_args=()
  if [[ "$key_case" == incorrect ]]; then
    header_args=(-H 'X-Northstar-Key: incorrect-key')
  fi
  status_code=$(curl --noproxy '*' --silent --show-error \
    --connect-timeout 1 --max-time 3 "${header_args[@]}" \
    -o "$check_dir/handover-$key_case.txt" -w '%{http_code}' \
    http://172.30.0.30:8080/handover)
  if [[ "$status_code" != 403 ]] || grep -Fq 'FLAG{' "$check_dir/handover-$key_case.txt"; then
    printf 'Handover with %s key must return 403 without a flag.\n' "$key_case" >&2
    exit 1
  fi
done

status_code=$(curl --noproxy '*' --silent --show-error \
  --connect-timeout 1 --max-time 3 \
  -H 'X-Northstar-Key: northstar-maintenance-42' \
  -o "$check_dir/handover-unlocked.txt" -w '%{http_code}' \
  http://172.30.0.30:8080/handover)
if [[ "$status_code" != 200 ]]; then
  printf 'Handover with the correct key must return 200.\n' >&2
  exit 1
fi
grep -Fxq 'FLAG{open_port_is_not_a_service}' "$check_dir/handover-unlocked.txt"

status_code=$(curl --noproxy '*' --silent --show-error \
  --connect-timeout 1 --max-time 3 \
  -o "$check_dir/unknown-path.txt" -w '%{http_code}' \
  http://172.30.0.30:8080/not-a-real-handover)
if [[ "$status_code" != 404 ]]; then
  printf 'An unknown status path must return 404.\n' >&2
  exit 1
fi

jq -e '.synthetic == true and (.matches | length == 3)' \
  /opt/lab2/snapshot.json >/dev/null
printf 'PASS: expected ZMap hits, three CTF flags, handover gate and snapshot verified.\n'
