"""Client: calls the Inventory Service by its Kubernetes Service NAME, once per second.

It never uses Pod IPs. Kubernetes DNS resolves "inventory-service" to the Service's
stable ClusterIP, and kube-proxy forwards each new connection to one READY Pod.
Each line logs which Pod answered, so you can see traffic spread across replicas.
"""
import json
import os
import time
import urllib.request
from datetime import datetime

URL = os.getenv("INVENTORY_URL", "http://inventory-service/inventory")
INTERVAL = float(os.getenv("INTERVAL", "1"))

print(f"client starting, target = {URL}", flush=True)
n = 0
while True:
    n += 1
    ts = f"{datetime.now():%H:%M:%S}"
    try:
        # A new connection per request, so each request is load-balanced independently.
        with urllib.request.urlopen(URL, timeout=2) as resp:
            body = json.loads(resp.read())
        print(f"{ts} req#{n:03d} 200 served-by={body['pod']} ({body['pod_ip']})", flush=True)
    except Exception as e:
        print(f"{ts} req#{n:03d} ERROR {e}", flush=True)
    time.sleep(INTERVAL)
