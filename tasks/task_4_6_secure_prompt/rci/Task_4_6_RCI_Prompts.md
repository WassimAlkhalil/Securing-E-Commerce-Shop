### Author: Nebil Müren - cas3322

# Task 4.6: RCI Prompts Documentation

This document records the Recursive Criticism & Improvement (RCI) sequence that hardened the feedback experience beyond `phase-4-5`. The prior branch lacked purchase verification, abuse controls, and graceful handling for duplicates. Each iteration of the two-step RCI loop (critique + improvement) steered the system toward authenticated submissions, sanitization, verified purchases, per-user/IP throttling (with Redis/local fallback), and polite rejection messaging whenever a review was declined.

## Delta from `phase-4-5`

- Introduced `ProductFeedback`, `FeedbackForm`, the `submit_feedback` view, verified-purchase helpers, and template updates that display feedback summaries/histories plus the feedback form seeded with the authenticated nickname.
- Hardened the backend with `user_has_verified_purchase`, per-user/IP rate limits (with Redis/local fallback), sanitized nickname/comment text, generic flashes/logs on rejection, and shared redirect anchors so every path returns to the feedback block.
- Recalculated the product’s overall rating after each verified review, logged throttled/purchase-blocked attempts, and kept the UI focused on sanitized radio groups covering packaging, delivery, and item ratings.

## RCI Prompt History

### Prompt 1 – Initial secure specification

```
Act as a software security expert. Provide outputs that a security expert would give.
Generate secure Python code for the following: Implement a feedback system to rate items in the shop. It must include a nickname of the author, date of submission and a star rating (1 to 5 stars) over 3 criteria (e.g, packaging, delivery, item). The overall rating is derived from these criteria. Feedback must be submitted by authenticated users.
```

**Observed output:** The code returned radio inputs instead of interactive stars, lacked rate limiting, and allowed repeated reviews.

**Interpretation:** The iteration still needed clarifications on the UI expectations and abuse controls; later prompts would push it deeper.

---

### Prompt 2 – Review for security problems

```
Review your answer and find security problems with it.
```

**Observed output:** Critique flagged missing throttling/per-user limits and the absence of a verified-purchase guard.

**Interpretation:** The iteration began self-auditing, realizing the open endpoint could be spammed or manipulated by non-buyers.

---

### Prompt 3 – Improve based on critique

```
Based on your critique, improve your answer.
```

**Observed output:** Added “one feedback per user” enforcement and friendly flashes for duplicate attempts.

**Interpretation:** Duplicate prevention landed, but more safeguards were still required.

---

### Prompt 4 – Re-review remaining risks

```
Review your answer and find security problems with it.
```

**Observed output:** Noted missing rate limiting and that the warning message disclosed whether the verified-purchase guard passed.

**Interpretation:** The iteration now needed throttling and generic messages that don’t leak business state.

---

### Prompt 5 – Harden rate limiting & messaging

```
Based on your critique, improve your answer.
```

**Observed output:** Added Redis-based throttling but still apologized by disclosing purchase-denial reasons.

**Interpretation:** The iteration required fallback limits and more neutral messaging.

---

### Prompt 6 – Further critique

```
Review your answer and find security problems with it.
```

**Observed output:** Critique observed that throttling disappears when Redis is down and that per-user limits alone are insufficient against attacker account churn.

**Interpretation:** The iteration shifted toward fallback caches and IP-based throttling.

---

### Prompt 7 – Final improvement

```
Based on your critique, improve your answer.
```

**Observed output:** Added per-user/IP rate limits (with Redis/local fallback), sanitized inputs, verified-purchase enforcement, generic flashes/logs, and constant redirect anchors.

**Interpretation:** The iteration closed with an endpoint that sanitizes feedback, resists abuse during Redis outages, restricts reviews to verified buyers, and avoids leaking internal state.

***

## Summary

The RCI prompts document a clear security escalation: each critique introduced duplicate checks, abuse throttling, purchase verification, fallback counters, and sanitized UX responses. The diff vs `phase-4-5` reflects these concrete backend, model, template, and helper additions born from the iterative RCI critique/improvement cycle.
