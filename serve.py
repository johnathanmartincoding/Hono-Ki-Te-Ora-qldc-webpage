"""
serve.py - serves a folder on your local network so you can test the website
from your phone, tablet or another computer, not just this machine.

Usage:
    python serve.py                      (serves the folder the script is in)
    python serve.py "C:\\path\\to\\folder"  (serves that folder)
    python serve.py -p 9000              (use a different port)
    python serve.py --page other.html    (open a different page on start)
    python serve.py --local-only         (old behaviour: only this computer can connect)

Prints a network address like http://192.168.1.23:8000/ - open that on any
phone or tablet connected to the SAME wifi network as this computer.
Ctrl+C to stop. Files are re-read on every refresh, so edits show up straight away.
"""
import argparse
import functools
import http.server
import os
import socket
import socketserver
import webbrowser


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def local_ip():
    """Best-guess LAN IP - doesn't actually send anything, just picks the interface."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


ap = argparse.ArgumentParser()
ap.add_argument("folder", nargs="?", default=os.path.dirname(os.path.abspath(__file__)))
ap.add_argument("-p", "--port", type=int, default=8000)
ap.add_argument("--page", default="central-lakes-directory.html", help="page to open on start")
ap.add_argument("--no-browser", action="store_true", help="don't open the browser automatically")
ap.add_argument("--local-only", action="store_true", help="only allow this computer to connect")
args = ap.parse_args()

folder = os.path.abspath(args.folder)
if not os.path.isdir(folder):
    raise SystemExit(f"Not a folder: {folder}")

handler = functools.partial(NoCacheHandler, directory=folder)
socketserver.TCPServer.allow_reuse_address = True
bind_host = "127.0.0.1" if args.local_only else "0.0.0.0"

# if the port is busy, try the next few
for port in range(args.port, args.port + 10):
    try:
        server = socketserver.TCPServer((bind_host, port), handler)
        break
    except OSError:
        print(f"Port {port} is busy, trying the next one...")
else:
    raise SystemExit("Couldn't find a free port.")

page = args.page if os.path.isfile(os.path.join(folder, args.page)) else ""
local_url = f"http://localhost:{port}/{page}"
print(f"Serving {folder}\n")
print(f"On this computer:  {local_url}")
if not args.local_only:
    print(f"On your phone/tablet (same wifi): http://{local_ip()}:{port}/{page}")
    print("\nIf the phone can't connect, check this computer's firewall isn't blocking Python,")
    print("and that the phone is on the same wifi network (not mobile data).")
print("\nCtrl+C to stop\n")
if not args.no_browser:
    webbrowser.open(local_url)

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nStopped.")
finally:
    server.server_close()
