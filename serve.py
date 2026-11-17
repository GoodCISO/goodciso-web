#!/usr/bin/env python3
"""Serve each built site at its own root, exactly as Netlify will.

The four sites deploy to four separate Netlify sites, so each has its own
document root. Serving them from one directory with a shared prefix would
mis-resolve root-absolute asset paths and give a false rendering result.
"""
import sys
import threading
from functools import partial
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

SITES = [
    (8901, "dist/aware"),
    (8902, "dist/corporate"),
    (8903, "dist/docs"),
    (8904, "dist/demo"),
]

ROOT = str(Path(__file__).parent.resolve())


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def serve(port, directory):
    handler = partial(Handler, directory=f"{ROOT}/{directory}")
    httpd = ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


if __name__ == "__main__":
    servers = [serve(p, d) for p, d in SITES]
    print("serving:", ", ".join(f"http://127.0.0.1:{p} -> {d}" for p, d in SITES))
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
