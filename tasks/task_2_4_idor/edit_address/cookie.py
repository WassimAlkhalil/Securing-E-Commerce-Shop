import requests

s = requests.Session()
s.cookies.set("session", "eyJ1c2VyX2lkIjoxLCJhbm90aGVyIjoi..." )
resp = s.get("http://127.0.0.1:5000/account/address/edit?id=12")
print(resp.status_code)
print(resp.text[:500])
