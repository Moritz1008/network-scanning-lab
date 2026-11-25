#!/bin/sh
# Start the broker, then publish retained sensor values and the stage 6 flag.
# Only our config: Debian's default one wants a pid file in /run/mosquitto.
mosquitto -c /etc/mosquitto/conf.d/lab.conf &
BROKER=$!
i=0
until mosquitto_pub -h ::1 -r -t coolcorp/hq/status -m "sensor hub online" 2>/dev/null; do
  i=$((i + 1))
  [ "$i" -ge 20 ] && { echo "[mqtt] broker did not start" >&2; exit 1; }
  sleep 0.5
done
mosquitto_pub -h ::1 -r -t coolcorp/hq/coldroom1/temp -m "-18.4"
mosquitto_pub -h ::1 -r -t coolcorp/hq/coldroom2/temp -m "-21.0"
mosquitto_pub -h ::1 -r -t coolcorp/hq/coldroom1/door -m "closed"
mosquitto_pub -h ::1 -r -t coolcorp/hq/maintenance/token -m "STAGE 6 MQTT FLAG: $FLAG_MQTT"
echo "[mqtt] broker up on [::]:1883, retained topics published"
wait "$BROKER"
