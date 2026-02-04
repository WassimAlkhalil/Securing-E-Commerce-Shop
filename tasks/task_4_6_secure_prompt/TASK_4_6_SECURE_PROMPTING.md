### Author: Nebil Müren - cas3322

# Task 4.6.b — Secure Prompting (Persona + RCI)

This report compares the prompts used in **Task 4.4** with prompting techniques from Section 4 of *Prompting Techniques for Secure Code Generation*, and evaluates two improved prompting techniques (Persona and RCI) from a security perspective.

---

## 1) Task Context

**Task 4.4:** Implement a feedback system with nickname, date, star ratings (1-5) for packaging/delivery/item, and overall rating. Must be authenticated.

**Task 4.5:** Assess security using Bandit and document findings.

**Task 4.6:** Compare Task 4.4 prompts with Section 4 techniques, select two techniques, and evaluate security improvements.

---

## 2) Baseline: Task 4.4 Prompting Strategy

**Classification:** Zero-shot prompting with human-driven iterative refinement (not structured RCI loop).

**Prompts:**
1. Initial secure implementation request
2. UI enhancement
3. Star rating implementation
4. Security/business logic (one feedback per user)

**Summary:** Incremental refinement. Security intent existed but requirements emerged via later refinement rather than structured secure prompting.

---

## 3) Task 4.5 — Bandit Assessment (Baseline)

**Bandit findings:** No issues reported.

**Critical Security Vulnerabilities (Post-Bandit Analysis):**
- ❌ **XSS Vulnerability:** No input sanitization
- ⚠️ **Rate Limiting Weakness:** Basic (5/hour, user only, no IP protection)
- ❌ **No Purchase Verification:** Anyone can review
- ⚠️ **Information Disclosure:** Specific error messages
- ❌ **No Fallback:** Rate limiting fails if Redis down

**Security Score: 4/10** — **NOT PRODUCTION READY**

---

## 4) Selected Prompting Techniques

**Technique #1: Persona (Priming)** — Primes LLM with "security expert" role to influence secure decisions.

**Technique #2: RCI (Recursive Criticism and Improvement)** — Structured loop: generate → critique → improve → repeat.

---

## 5) Persona Technique Results

### 5.1 Prompt Sequence
1. Secure star rating clarification (still produced numeric inputs)
2. Enforce single feedback (raw SQLAlchemy error surfaced)
3. Graceful duplicate rejection (fixed exception leakage)

### 5.2 Outcome
**Improvements:**
- ✅ Exception handling (no raw error leakage)
- ✅ Duplicate prevention
- ✅ Interactive star UI

**Security Gaps:**
- ❌ No input sanitization (XSS risk)
- ❌ No rate limiting
- ❌ No purchase verification
- ⚠️ Information disclosure

**Security Score: 5/10** — Improved exception handling but missing critical features.

**Bandit:** No findings (but misses application-layer security).

---

## 6) RCI Technique Results

### 6.1 Prompt Sequence (7 iterations)
1. Initial secure specification → Radio inputs, no throttling
2. Critique → Missing abuse controls, purchase verification
3. Improve → Added duplicate prevention
4. Critique → Missing rate limiting, information disclosure
5. Improve → Added Redis throttling (still leaks reasons)
6. Critique → No fallback, weak against account churn
7. Final → Per-user/IP throttling, Redis/local fallback, sanitization, purchase verification, generic messages

### 6.2 Outcome
**Security Improvements:**
- ✅ Input sanitization (bleach) — XSS protection
- ✅ Advanced rate limiting (5/user + 20/IP per 60s) with Redis/local fallback
- ✅ Purchase verification (verified orders only)
- ✅ Generic error messages (prevents enumeration)
- ✅ Security logging
- ✅ Duplicate prevention
- ✅ Fail-safe design

**Security Score: 9/10** — **PRODUCTION READY**

**Bandit:** No findings, but RCI discovered critical application-layer security features.

---

## 7) Security Comparison

### 7.1 Bandit Results
| Variant | Bandit Findings | Interpretation |
|---------|----------------|----------------|
| Task 4.4 baseline | None | Bandit-clean |
| Task 4.6 Persona | None | Improved exception handling |
| Task 4.6 RCI | None | Stronger abuse controls |

**Result:** Bandit found no issues in any variant, but Persona and RCI improved robustness beyond static analysis scope.

### 7.2 Comprehensive security feature comparison
| Security Feature | Task 4.4 Baseline | Task 4.6 Persona | Task 4.6 RCI |
|-----------------|-------------------|-------------------|--------------|
| **Input Sanitization** | ❌ None (XSS risk) | ❌ None (XSS risk) | ✅ Bleach sanitization |
| **Rate Limiting** | ✅ Basic (5/hour, user only) | ❌ None | ✅ Advanced (5/user + 20/IP per 60s) |
| **Rate Limiting Fallback** | ❌ No (fails if Redis down) | ❌ N/A | ✅ Local in-memory fallback |
| **Purchase Verification** | ❌ None | ❌ None | ✅ Required (verified orders only) |
| **Duplicate Prevention** | ✅ DB constraint + query | ✅ DB constraint + query | ✅ DB constraint + query |
| **XSS Protection** | ❌ No | ❌ No | ✅ Yes (bleach) |
| **CSRF Protection** | ✅ Flask-WTF | ✅ Flask-WTF | ✅ Flask-WTF |
| **Information Disclosure** | ⚠️ Specific messages | ⚠️ Specific messages | ✅ Generic messages |
| **IP-based Rate Limiting** | ❌ No | ❌ No | ✅ Yes |
| **Security Logging** | ⚠️ Basic | ⚠️ Basic | ✅ Comprehensive |
| **Exception Handling** | ⚠️ Broad catch-all | ✅ Graceful handling | ✅ Graceful handling |
| **Fail-Safe Design** | ❌ No | ⚠️ Partial | ✅ Yes |

### 7.3 Security Scores
| Variant | Score | Production Ready? | Critical Issues |
|---------|-------|-------------------|----------------|
| Baseline | 4/10 | ❌ | XSS, weak rate limiting, no purchase verification |
| Persona | 5/10 | ❌ | No sanitization, no rate limiting, no purchase verification |
| RCI | 9/10 | ✅ | Minor: partial database indexing |

### 7.4 Key Insight
RCI's iterative self-critique discovered security vulnerabilities (input sanitization, rate limiting, purchase verification, information disclosure, fallback mechanisms) that Persona (even with "security expert" role) did not identify.

---

## 8) Conclusion

### 8.1 Effectiveness
- **Baseline (Zero-shot):** 4/10 — Critical XSS vulnerability
- **Persona:** 5/10 — Better exception handling, but missing critical features
- **RCI:** 9/10 — Comprehensive security implementation

### 8.2 Key Findings
**Bandit Limitations:** Static analysis missed critical vulnerabilities (XSS, rate limiting, purchase verification).

**RCI Superiority:** Iterative critique-improvement loop more effective than Persona for discovering security requirements. RCI discovered:
- Input sanitization (XSS protection)
- Rate limiting (abuse prevention)
- Purchase verification (review authenticity)
- Information disclosure fixes (enumeration prevention)
- Fallback mechanisms (resilience)

### 8.3 Recommendations
**For Secure Code Generation:**
1. Use RCI for security-critical features
2. Combine Persona with RCI (Persona for initial focus, RCI for discovery)
3. Don't rely solely on static analysis
4. Explicit security requirements help (e.g., "find security problems")

**For Production:**
- Baseline: ❌ NOT PRODUCTION READY
- Persona: ❌ NOT PRODUCTION READY
- RCI: ✅ PRODUCTION READY

### 8.4 Final Assessment
RCI demonstrated superior effectiveness for security-focused code generation. The iterative self-critique process proved more valuable than role-based priming alone, suggesting **explicit security critique loops** are essential for generating secure code with LLMs.
