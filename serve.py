"""
World Cup 2026 schedule server.

Serves this folder AND persists match scores to scores.json, making that file
the single source of truth. Both HTML pages load scores.json on startup and
POST updates to /save as you type.

Run:  python serve.py   (or double-click start-worldcup.bat)
Then open http://localhost:8742/worldcup-2026-live.html
"""
import json
import os
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.dirname(os.path.abspath(__file__))
SCORES = os.path.join(ROOT, "scores.json")
PORT = 8742
WRITE_LOCK = threading.Lock()


class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path.rstrip("/") == "/save":
            try:
                n = int(self.headers.get("Content-Length", 0))
                data = json.loads(self.rfile.read(n).decode("utf-8"))
                if not isinstance(data, dict):
                    raise ValueError("scores payload must be a JSON object")
            except (ValueError, json.JSONDecodeError):
                self.send_response(400)
                self.end_headers()
                return
            with WRITE_LOCK:
                tmp = SCORES + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=1, sort_keys=True)
                os.replace(tmp, SCORES)  # atomic so a crash can't corrupt the file
            self.send_response(204)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def end_headers(self):
        # scores.json must never be served stale
        if "scores.json" in self.path:
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        if "/save" not in (args[0] if args else ""):
            super().log_message(fmt, *args)


if __name__ == "__main__":
    os.chdir(ROOT)
    if not os.path.exists(SCORES):
        with open(SCORES, "w", encoding="utf-8") as f:
            f.write("{}")
    print(f"World Cup server running — http://localhost:{PORT}/worldcup-2026-live.html", flush=True)
    print(f"Scores are stored in {SCORES}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
