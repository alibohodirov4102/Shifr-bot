"""
Keep Alive Server — Serverlarda (Render, Koyeb, Railway va boshqalar)
bot 24/7 ishlab turishi uchun yengil HTTP server.
"""

import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging

logger = logging.getLogger(__name__)

class SimpleHealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.end_headers()
        response = '{"status": "ok", "bot": "Shifr Bot 24/7 faol"}'
        self.wfile.write(response.encode("utf-8"))

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        pass

def run_server(port: int):
    try:
        server_address = ("0.0.0.0", port)
        httpd = HTTPServer(server_address, SimpleHealthCheckHandler)
        logger.info(f"🌐 Keep-Alive server {port}-portda ishga tushdi")
        httpd.serve_forever()
    except Exception as e:
        logger.warning(f"Keep-Alive server ishga tushishida ogohlantirish: {e}")

def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    t = threading.Thread(target=run_server, args=(port,), daemon=True)
    t.start()
