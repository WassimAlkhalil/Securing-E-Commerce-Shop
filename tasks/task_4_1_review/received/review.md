# Code Review of all Bandit Issues for Group 3

[TOC]

## Test_ID

### B101, assert_used
- Issue number: 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41
- This issue is a false positive.
- The usage of asserts in the test files is unproblematic.
- The Issue would be in the optimisation of python code, so in production code the assert could be unintentionally removed.
- The better choice in production code would be the throwing of errors.

### B105, hardcoded_password_string
- Issue number: 23, 30
- In Issue 23: The client secret of PayPal was hardcoded in the setting.py file, it would be better to include it in a .env file.
- In Issue 30: This is a bit less problematic due to the usage in tests only.

### B106, hardcoded_password_funcarg
- Issue number: 15, 16, 17, 18
- For all the issues, this is regarding random/seed data that would usually not entered like this in to the system and not used like this in production.

### B310, blacklist
- Issue number: 24, 27
- urllib like used in both code files could accept the file:// scheme.
- Either check explicit for http/https or use the requests library

### B111, blacklist
- Issue number: 1, 6, 7, 9, 10, 11, 12, 13, 18, 19, 20, 21, 22
- For 9-13 and 18-22: It isn't really an issue as the pseudo random generator is just used to generate the random seed data.
- In issue 1 the reset password generator is insecure so we could guess the generated reset password. It is better to use the secrets library here, instead of random.
- In issue 6 and 7, this is a false positive, the random generated int is just used to be part of the object identification, especially due to the lower overhead of random (There is a low possibility of collosion).

### B403, blacklist
- Issue 5
- Well we don't think that pickkle is here the issue, due to redis needing to be compromised, else the standard python json packages could be used, if everything is unserializable.

### B404, blacklist, B602, B603, subprocess
- Issue 2, 3, 4
- The issue is there to prevent code injection, but due to only using  static, trusted values (pytest and constant TEST_PATH). No user input is involved. Risk is negligible

### B704, markupsafe_markup_xss
- Issue 8
- The Markup here is unescaped, just escape it

### B608, hardcoded_sql_expressions
- Issue 25,26,28,29
- I mean they are SQLi scripts, so it is the whole point. Else it should be a prepared statement and not string interpolation.
- False positive

## Table of Issues

| # | filename | test_name | test_id | issue_severity | issue_confidence | issue_cwe | issue_text | line_number | col_offset | end_col_offset | line_range | more_info |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | softsec-shop/flaskshop/account/utils.py | blacklist | B311 | LOW | HIGH | https://cwe.mitre.org/data/definitions/330.html | Standard pseudo-random generators are not suitable for security/cryptographic purposes. | 155 | 19 | 39 | [155] | https://bandit.readthedocs.io/en/1.9.2/blacklists/blacklist_calls.html#b311-random |
| 2 | softsec-shop/flaskshop/commands.py | blacklist | B404 | LOW | HIGH | https://cwe.mitre.org/data/definitions/78.html | Consider possible security implications associated with the subprocess module. | 6 | 0 | 27 | [6] | https://bandit.readthedocs.io/en/1.9.2/blacklists/blacklist_imports.html#b404-import-subprocess |
| 3 | softsec-shop/flaskshop/commands.py | subprocess_popen_with_shell_equals_true | B602 | HIGH | HIGH | https://cwe.mitre.org/data/definitions/78.html | subprocess call with shell=True identified, security issue. | 41 | 10 | 49 | [41] | https://bandit.readthedocs.io/en/1.9.2/plugins/b602_subprocess_popen_with_shell_equals_true.html |
| 4 | softsec-shop/flaskshop/commands.py | subprocess_without_shell_equals_true | B603 | LOW | HIGH | https://cwe.mitre.org/data/definitions/78.html | subprocess call - check for execution of untrusted input. | 68 | 13 | 31 | [68] | https://bandit.readthedocs.io/en/1.9.2/plugins/b603_subprocess_without_shell_equals_true.html |
| 5 | softsec-shop/flaskshop/corelib/mc.py | blacklist | B403 | LOW | HIGH | https://cwe.mitre.org/data/definitions/502.html | Consider possible security implications associated with UnpicklingError module. | 3 | 0 | 34 | [3] | https://bandit.readthedocs.io/en/1.9.2/blacklists/blacklist_imports.html#b403-import-pickle |
| 6 | softsec-shop/flaskshop/corelib/utils.py | blacklist | B311 | LOW | HIGH | https://cwe.mitre.org/data/definitions/330.html | Standard pseudo-random generators are not suitable for security/cryptographic purposes. | 28 | 11 | 38 | [28] | https://bandit.readthedocs.io/en/1.9.2/blacklists/blacklist_calls.html#b311-random |
| 7 | softsec-shop/flaskshop/discount/models.py | blacklist | B311 | LOW | HIGH | https://cwe.mitre.org/data/definitions/330.html | Standard pseudo-random generators are not suitable for security/cryptographic purposes. | 52 | 23 | 67 | [52] | https://bandit.readthedocs.io/en/1.9.2/blacklists/blacklist_calls.html#b311-random |
| 8 | softsec-shop/flaskshop/plugin/utils.py | markupsafe_markup_xss | B704 | MEDIUM | HIGH | https://cwe.mitre.org/data/definitions/79.html | Potential XSS with ``markupsafe.Markup`` detected. Do not use ``Markup`` on untrusted data. | 38 | 15 | 29 | [38] | https://bandit.readthedocs.io/en/1.9.2/plugins/b704_markupsafe_markup_xss.html |
| 9 | softsec-shop/flaskshop/random_data.py | blacklist | B311 | LOW | HIGH | https://cwe.mitre.org/data/definitions/330.html | Standard pseudo-random generators are not suitable for security/cryptographic purposes. | 45 | 15 | 56 | [45] | https://bandit.readthedocs.io/en/1.9.2/blacklists/blacklist_calls.html#b311-random |
| 10 | softsec-shop/flaskshop/random_data.py | blacklist | B311 | LOW | HIGH | https://cwe.mitre.org/data/definitions/330.html | Standard pseudo-random generators are not suitable for security/cryptographic purposes. | 244 | 43 | 65 | [244] | https://bandit.readthedocs.io/en/1.9.2/blacklists/blacklist_calls.html#b311-random |
| 11 | softsec-shop/flaskshop/random_data.py | blacklist | B311 | LOW | HIGH | https://cwe.mitre.org/data/definitions/330.html | Standard pseudo-random generators are not suitable for security/cryptographic purposes. | 286 | 23 | 44 | [286] | https://bandit.readthedocs.io/en/1.9.2/blacklists/blacklist_calls.html#b311-random |
| 12 | softsec-shop/flaskshop/random_data.py | blacklist | B311 | LOW | HIGH | https://cwe.mitre.org/data/definitions/330.html | Standard pseudo-random generators are not suitable for security/cryptographic purposes. | 296 | 16 | 55 | [296] | https://bandit.readthedocs.io/en/1.9.2/blacklists/blacklist_calls.html#b311-random |
| 13 | softsec-shop/flaskshop/random_data.py | blacklist | B311 | LOW | HIGH | https://cwe.mitre.org/data/definitions/330.html | Standard pseudo-random generators are not suitable for security/cryptographic purposes. | 307 | 21 | 68 | [307] | https://bandit.readthedocs.io/en/1.9.2/blacklists/blacklist_calls.html#b311-random |
| 14 | softsec-shop/flaskshop/random_data.py | hardcoded_password_funcarg | B106 | LOW | MEDIUM | https://cwe.mitre.org/data/definitions/259.html | Possible hardcoded password: 'password' | 357 | 14 | 5 | [357, 358, 359, 360, 361, 362] | https://bandit.readthedocs.io/en/1.9.2/plugins/b106_hardcoded_password_funcarg.html |
| 15 | softsec-shop/flaskshop/random_data.py | hardcoded_password_funcarg | B106 | LOW | MEDIUM | https://cwe.mitre.org/data/definitions/259.html | Possible hardcoded password: 'admin' | 389 | 11 | 5 | [389, 390, 391] | https://bandit.readthedocs.io/en/1.9.2/plugins/b106_hardcoded_password_funcarg.html |
| 16 | softsec-shop/flaskshop/random_data.py | hardcoded_password_funcarg | B106 | LOW | MEDIUM | https://cwe.mitre.org/data/definitions/259.html | Possible hardcoded password: 'op' | 397 | 11 | 88 | [397] | https://bandit.readthedocs.io/en/1.9.2/plugins/b106_hardcoded_password_funcarg.html |
| 17 | softsec-shop/flaskshop/random_data.py | hardcoded_password_funcarg | B106 | LOW | MEDIUM | https://cwe.mitre.org/data/definitions/259.html | Possible hardcoded password: 'editor' | 400 | 11 | 5 | [400, 401, 402] | https://bandit.readthedocs.io/en/1.9.2/plugins/b106_hardcoded_password_funcarg.html |
| 18 | softsec-shop/flaskshop/random_data.py | blacklist | B311 | LOW | HIGH | https://cwe.mitre.org/data/definitions/330.html | Standard pseudo-random generators are not suitable for security/cryptographic purposes. | 502 | 13 | 50 | [502] | https://bandit.readthedocs.io/en/1.9.2/blacklists/blacklist_calls.html#b311-random |
| 19 | softsec-shop/flaskshop/random_data.py | blacklist | B311 | LOW | HIGH | https://cwe.mitre.org/data/definitions/330.html | Standard pseudo-random generators are not suitable for security/cryptographic purposes. | 519 | 49 | 71 | [519] | https://bandit.readthedocs.io/en/1.9.2/blacklists/blacklist_calls.html#b311-random |
| 20 | softsec-shop/flaskshop/random_data.py | blacklist | B311 | LOW | HIGH | https://cwe.mitre.org/data/definitions/330.html | Standard pseudo-random generators are not suitable for security/cryptographic purposes. | 536 | 15 | 37 | [536] | https://bandit.readthedocs.io/en/1.9.2/blacklists/blacklist_calls.html#b311-random |
| 21 | softsec-shop/flaskshop/random_data.py | blacklist | B311 | LOW | HIGH | https://cwe.mitre.org/data/definitions/330.html | Standard pseudo-random generators are not suitable for security/cryptographic purposes. | 553 | 13 | 52 | [553] | https://bandit.readthedocs.io/en/1.9.2/blacklists/blacklist_calls.html#b311-random |
| 22 | softsec-shop/flaskshop/random_data.py | blacklist | B311 | LOW | HIGH | https://cwe.mitre.org/data/definitions/330.html | Standard pseudo-random generators are not suitable for security/cryptographic purposes. | 581 | 23 | 58 | [581] | https://bandit.readthedocs.io/en/1.9.2/blacklists/blacklist_calls.html#b311-random |
| 23 | softsec-shop/flaskshop/settings.py | hardcoded_password_string | B105 | LOW | MEDIUM | https://cwe.mitre.org/data/definitions/259.html | Possible hardcoded password: 'EK2Ew3Zs7lVb1Y0DGOWWqWDKkaHPeZN5JmpLIfFZMgYf5J4bLzL2-c2Iwyi7x5LEtgXqFr5WYJZAGRXG' | 89 | 27 | 109 | [89] | https://bandit.readthedocs.io/en/1.9.2/plugins/b105_hardcoded_password_string.html |
| 24 | softsec-shop/tasks/task_2_3_sqli/brute_force_username.py | blacklist | B310 | MEDIUM | HIGH | https://cwe.mitre.org/data/definitions/22.html | Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected. | 15 | 15 | 42 | [15] | https://bandit.readthedocs.io/en/1.9.2/blacklists/blacklist_calls.html#b310-urllib-urlopen |
| 25 | softsec-shop/tasks/task_2_3_sqli/brute_force_username.py | hardcoded_sql_expressions | B608 | MEDIUM | LOW | https://cwe.mitre.org/data/definitions/89.html | Possible SQL injection vector through string-based query construction. | 20 | 20 | 79 | [20] | https://bandit.readthedocs.io/en/1.9.2/plugins/b608_hardcoded_sql_expressions.html |
| 26 | softsec-shop/tasks/task_2_3_sqli/brute_force_username.py | hardcoded_sql_expressions | B608 | MEDIUM | LOW | https://cwe.mitre.org/data/definitions/89.html | Possible SQL injection vector through string-based query construction. | 22 | 20 | 82 | [22] | https://bandit.readthedocs.io/en/1.9.2/plugins/b608_hardcoded_sql_expressions.html |
| 27 | softsec-shop/tasks/task_2_3_sqli/brute_force_vouchers.py | blacklist | B310 | MEDIUM | HIGH | https://cwe.mitre.org/data/definitions/22.html | Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected. | 15 | 15 | 42 | [15] | https://bandit.readthedocs.io/en/1.9.2/blacklists/blacklist_calls.html#b310-urllib-urlopen |
| 28 | softsec-shop/tasks/task_2_3_sqli/brute_force_vouchers.py | hardcoded_sql_expressions | B608 | MEDIUM | LOW | https://cwe.mitre.org/data/definitions/89.html | Possible SQL injection vector through string-based query construction. | 20 | 20 | 79 | [20] | https://bandit.readthedocs.io/en/1.9.2/plugins/b608_hardcoded_sql_expressions.html |
| 29 | softsec-shop/tasks/task_2_3_sqli/brute_force_vouchers.py | hardcoded_sql_expressions | B608 | MEDIUM | LOW | https://cwe.mitre.org/data/definitions/89.html | Possible SQL injection vector through string-based query construction. | 22 | 20 | 82 | [22] | https://bandit.readthedocs.io/en/1.9.2/plugins/b608_hardcoded_sql_expressions.html |
| 30 | softsec-shop/tests/settings.py | hardcoded_password_string | B105 | LOW | MEDIUM | https://cwe.mitre.org/data/definitions/259.html | Possible hardcoded password: 'not-so-secret-in-tests' | 7 | 13 | 37 | [7] | https://bandit.readthedocs.io/en/1.9.2/plugins/b105_hardcoded_password_string.html |
| 31 | softsec-shop/tests/test_config.py | assert_used | B101 | LOW | HIGH | https://cwe.mitre.org/data/definitions/703.html | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. | 10 | 4 | 38 | [10] | https://bandit.readthedocs.io/en/1.9.2/plugins/b101_assert_used.html |
| 32 | softsec-shop/tests/test_config.py | assert_used | B101 | LOW | HIGH | https://cwe.mitre.org/data/definitions/703.html | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. | 11 | 4 | 45 | [11] | https://bandit.readthedocs.io/en/1.9.2/plugins/b101_assert_used.html |
| 33 | softsec-shop/tests/test_config.py | assert_used | B101 | LOW | HIGH | https://cwe.mitre.org/data/definitions/703.html | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. | 12 | 4 | 50 | [12] | https://bandit.readthedocs.io/en/1.9.2/plugins/b101_assert_used.html |
| 34 | softsec-shop/tests/test_config.py | assert_used | B101 | LOW | HIGH | https://cwe.mitre.org/data/definitions/703.html | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. | 18 | 4 | 37 | [18] | https://bandit.readthedocs.io/en/1.9.2/plugins/b101_assert_used.html |
| 35 | softsec-shop/tests/test_database.py | assert_used | B101 | LOW | HIGH | https://cwe.mitre.org/data/definitions/703.html | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. | 29 | 8 | 68 | [29] | https://bandit.readthedocs.io/en/1.9.2/plugins/b101_assert_used.html |
| 36 | softsec-shop/tests/test_database.py | assert_used | B101 | LOW | HIGH | https://cwe.mitre.org/data/definitions/703.html | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. | 35 | 8 | 62 | [35] | https://bandit.readthedocs.io/en/1.9.2/plugins/b101_assert_used.html |
| 37 | softsec-shop/tests/test_database.py | assert_used | B101 | LOW | HIGH | https://cwe.mitre.org/data/definitions/703.html | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. | 42 | 8 | 58 | [42] | https://bandit.readthedocs.io/en/1.9.2/plugins/b101_assert_used.html |
| 38 | softsec-shop/tests/test_database.py | assert_used | B101 | LOW | HIGH | https://cwe.mitre.org/data/definitions/703.html | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. | 59 | 8 | 45 | [59] | https://bandit.readthedocs.io/en/1.9.2/plugins/b101_assert_used.html |
| 39 | softsec-shop/tests/test_database.py | assert_used | B101 | LOW | HIGH | https://cwe.mitre.org/data/definitions/703.html | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. | 68 | 8 | 56 | [68] | https://bandit.readthedocs.io/en/1.9.2/plugins/b101_assert_used.html |
| 40 | softsec-shop/tests/test_e2e.py | assert_used | B101 | LOW | HIGH | https://cwe.mitre.org/data/definitions/703.html | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. | 6 | 4 | 32 | [6] | https://bandit.readthedocs.io/en/1.9.2/plugins/b101_assert_used.html |
| 41 | softsec-shop/tests/test_e2e.py | assert_used | B101 | LOW | HIGH | https://cwe.mitre.org/data/definitions/703.html | Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. | 13 | 8 | 36 | [13] | https://bandit.readthedocs.io/en/1.9.2/plugins/b101_assert_used.html |
