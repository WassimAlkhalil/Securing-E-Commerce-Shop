# Password Strength Requirements

This application enforces strong password controls during user registration.  
All passwords must pass **three distinct validation checks** before an account is created.

> **Note:** Passwords are checked against both a local blacklist (`100k-most-used-passwords-NCSC.txt`) and the Have I Been Pwned (HIBP) API to prevent the use of previously breached passwords.

---

## Minimum Length

Passwords must be **at least 12 characters long**.

### Examples that PASS
- `CorrectHorse123`  
- `SecurePass789`

### Examples that FAIL
- `Test123!`  
- `Short1!`

---

## Character Variety Requirement

Passwords must include **at least 3 of the following 3 character types**  
*(special characters are optional per NIST)*:

- Uppercase letters (A–Z)  
- Lowercase letters (a–z)  
- Numbers (0–9)

### Examples that PASS
- `Abcdef1234`  
- `R3dDragonKing`

### Examples that FAIL (only two character types)
- `abcdefgh1234`  
- `AAAAAAAaaaaaa`  
- `123456789012`

---

## Block Common Passwords

The system rejects:
- Very common passwords  
- Frequently breached passwords  
- Simple sequences  

### Strong Alternatives
- `OceanSky2024`  
- `MySecurePass77`

### Examples that FAIL (blocked list)
- `password`  
- `123456`  
- `letmein123`

---

## Examples of Fully Valid Passwords

These meet all three rules: long, complex, not common.

- `SunsetSkyline88`  
- `GalaxyRunner2024`

---

## Examples of Invalid Passwords

- `123456789012` — too weak  
- `qwerty` — too common  
- `Abcdefgh123` — only 2 categories  



## Reference

- [NIST SP 800-63B: Digital Identity Guidelines – Authentication and Lifecycle](https://pages.nist.gov/800-63-3/sp800-63b.html)  
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

---

*Created by Swarup Bharat Phatangare*
