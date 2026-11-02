"""Inventory Service: a tiny HTTP server (Python standard library only).

Endpoints
  GET /inventory  -> stock list + which Pod answered (the Pod's hostname)
  GET /ready      -> 200 when ready, 503 when the file /tmp/not-ready exists
  GET /healthz    -> always 200 (the process is alive)

Readiness toggle (used in the readiness test):
  kubectl exec <pod> -- touch /tmp/not-ready   # Pod fails readiness
  kubectl exec <pod> -- rm /tmp/not-ready      # Pod becomes ready again
"""
import json
import os
import socket
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

POD_NAME = os.getenv("POD_NAME", socket.gethostname())
POD_IP = os.getenv("POD_IP", "unknown")
NOT_READY_FLAG = "/tmp/not-ready"
PORT = int(os.getenv("PORT", "8080"))

STOCK = {"SKU-APPLE": 120, "SKU-BANANA": 80, "SKU-COFFEE": 45, "SKU-MILK": 60}


def log(msg):
    print(f"{datetime.now():%H:%M:%S} [{POD_NAME}] {msg}", flush=True)


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/inventory":
            log(f"served /inventory to {self.client_address[0]}")
            self._send(200, {"pod": POD_NAME, "pod_ip": POD_IP, "stock": STOCK})
        elif self.path == "/ready":
            if os.path.exists(NOT_READY_FLAG):
                self._send(503, {"pod": POD_NAME, "ready": False})
            else:
                self._send(200, {"pod": POD_NAME, "ready": True})
        elif self.path == "/healthz":
            self._send(200, {"pod": POD_NAME, "alive": True})
        else:
            self._send(404, {"error": "not found"})

    def log_message(self, *args):   # silence default per-request access log (probes are noisy)
        pass


if __name__ == "__main__":
    log(f"Inventory Service starting on port {PORT} (pod_ip={POD_IP})")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
