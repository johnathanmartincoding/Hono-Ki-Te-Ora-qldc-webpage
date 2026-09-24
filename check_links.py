"""
check_links.py - tests every service/resource website link in data.json.

Usage: python check_links.py

Writes link_report.csv with one row per link: status, redirect target, notes.
Network access can't run in this sandbox, so this checks structure (duplicates,
malformed URLs, http vs https, same link reused for different services) and
leaves a column for you to fill in the real HTTP status once you run it with
real internet access (which the ADL laptops will have).
"""
import csv, json, socket
from urllib.parse import urlparse

d = json.load(open("data.json", encoding="utf-8"))
items = [{**s, "kind": "service"} for s in d["services"]] + [{**r, "kind": "resource"} for r in d["resources"]]

rows = []
seen = {}
for it in items:
    url = (it.get("website") or "").strip()
    name = it["name"]
    if not url:
        rows.append([name, it["kind"], "", "NO LINK", ""])
        continue
    p = urlparse(url)
    problem = ""
    if p.scheme != "https":
        problem = "not https"
    elif not p.netloc:
        problem = "malformed URL"
    seen.setdefault(url, []).append(name)
    rows.append([name, it["kind"], url, "TO TEST" if not problem else problem, ""])

# flag a link only when it's shared by DIFFERENTLY named listings (the same service
# repeated across towns sharing one link is normal, not a problem)
dupe_note = {}
for u, names in seen.items():
    uniq = sorted(set(names))
    if len(uniq) > 1:
        dupe_note[u] = "CHECK: same link used by different services - " + " / ".join(uniq)
for r in rows:
    if r[2] in dupe_note:
        r[4] = dupe_note[r[2]]

with open("link_report.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Service/Resource", "Type", "URL", "Status (fill in after opening)", "Notes"])
    w.writerows(rows)

print(f"{len(rows)} rows written to link_report.csv")
print(f"{sum(1 for r in rows if r[3]=='NO LINK')} listings have no link")
print(f"{len(dupe_note)} links are shared by more than one listing")
