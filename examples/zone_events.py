#!/usr/bin/env python3
"""Turn raw RFID reads from MQTT into ENTER/EXIT zone events.

Expected raw message (JSON) on topic rfid/raw/<zone>:
    {"tag": "E2801160...", "rssi": -52, "ts": 1731400000.123}

Publishes events on rfid/events/<zone>.
pip install paho-mqtt
"""
import json
import time
from collections import defaultdict, deque

import paho.mqtt.client as mqtt

BROKER = "localhost"
MIN_READS = 2          # reads needed within WINDOW to accept presence
WINDOW = 1.5           # seconds
EXIT_TIMEOUT = 5.0     # seconds without reads -> tag left the zone
REENTRY_BLOCK = 60.0   # seconds; ignore re-entry bounce at zone edge

recent = defaultdict(deque)   # (zone, tag) -> timestamps of recent reads
present = {}                  # (zone, tag) -> last read time
last_exit = {}                # (zone, tag) -> exit time


def publish(client, zone, kind, tag, ts):
    client.publish(f"rfid/events/{zone}", json.dumps({"event": kind, "tag": tag, "ts": ts}))


def on_message(client, _userdata, msg):
    zone = msg.topic.rsplit("/", 1)[-1]
    data = json.loads(msg.payload)
    tag, ts = data["tag"], float(data.get("ts", time.time()))
    key = (zone, tag)

    if key in present:
        present[key] = ts
        return

    reads = recent[key]
    reads.append(ts)
    while reads and ts - reads[0] > WINDOW:
        reads.popleft()

    if len(reads) >= MIN_READS and ts - last_exit.get(key, 0) > REENTRY_BLOCK:
        present[key] = ts
        reads.clear()
        publish(client, zone, "ENTER", tag, ts)


def sweep(client):
    now = time.time()
    for key, seen in list(present.items()):
        if now - seen > EXIT_TIMEOUT:
            zone, tag = key
            del present[key]
            last_exit[key] = now
            publish(client, zone, "EXIT", tag, now)


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    client.connect(BROKER)
    client.subscribe("rfid/raw/+")
    client.loop_start()
    try:
        while True:
            sweep(client)
            time.sleep(0.5)
    finally:
        client.loop_stop()


if __name__ == "__main__":
    main()
