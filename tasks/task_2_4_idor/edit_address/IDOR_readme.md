# IDOR Miner — Short README

**Purpose:** Quickly test an IDOR vulnerability using the miner script in the `task` folder and verify the fix.

> **Ethics:** Run only on systems you own or are authorized to test.

## Quick steps

1. Activate venv and install deps:

```bash
python3 -m venv venv
source venv/bin/activate
pip install requests beautifulsoup4
```

2. Run the miner (before applying fix) to reproduce leakage:

```bash
python idor.miner.py    
```

3. Apply the access-control fix on the server (authorize `req.user.id == requested_id` or role-check for admins). See server-side examples in main docs.

4. Re-run the miner (after fix) to confirm mitigation:

```bash
python idor.miner.py    
```

5. Compare outputs: `before_fix.csv` should contain other users' data; `after_fix.csv` should not.


Created By Swarup Bharat Phatangare