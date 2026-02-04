### Author: Nebil Müren - cas3322

# Task 4.6: RCI Justification

## Where the code looks good

- **Authenticated submissions are sanitized and scoped**  
  - `FeedbackForm` keeps nicknames and comments constrained (`Length` validators) and only reflects integer choices (1-5) from dedicated radio groups, so Flask processes a predictable set of values even before the view-level sanitization.  
  - The view cleans the nickname/comment with `bleach` and never allows an anonymous POST—the endpoint routes through `@login_required` and repopulates the defaults with the user’s stored display name.

- **Database and business rules stop duplicate or non-purchase reviews**  
  - `ProductFeedback` now links `user_id` and stores the three criterion scores plus the derived overall rating; the ORM call is guarded by `ProductFeedback.query.filter_by(...)` and `user_has_verified_purchase` before any row reaches the session.  
  - These rules mean the database never sees duplicate rows or feedback from someone without a shipped/completed order, shrinking the attack window even if a client script tries to resubmit.

- **Abuse control works even when infrastructure falters**  
  - The feedback submission path checks both per-user and per-IP limits (5 and 20 submissions per 60 s) and prefers Redis-backed counters, but it falls back to an in-process windowed history when Redis is off or temporarily unreachable.  
  - The handler consistently redirects to the product anchor with friendly flashes/logs instead of leaking whether a user owned the product or whether the limit was hit, so enumeration is limited and the UX stays calm.

***

## Bandit report (`bandit-results-4-6-rci-prompt-4.html`)

- Total lines of code: 7,604 with 20 lines skipped for `#nosec`.  
- The report contains no findings—no issues were flagged in this scan—because the feedback additions keep data access within the ORM, wrap user input in sanitized fields, and rely on server-side CSRF/protection controls.  
- Since the static scan stayed quiet, we direct focus toward the application-layer guarantees (rate limiting, verified purchases, Redis availability) that live outside of Bandit’s view.

***

## Delta vs. phase-4-5

- **Forms & handler:** `FeedbackForm` now models the nickname, comment, and three criterion ratings with explicit string/radio fields. The `submit_feedback` view adds rate limiting (per user/IP) with Redis/local fallback, verifies actual purchases via `user_has_verified_purchase`, and sanitizes every user input before creating a `ProductFeedback` record.  
- **Models & helpers:** `ProductFeedback` tracks `user_id`, per-criterion ratings, and the derived overall score; `Product.feedbacks` plus `feedback_summary` expose the latest entries and aggregate rating, and the new helper `user_has_verified_purchase` reuses `OrderLine` joins/`OrderStatusKinds` to enforce that only fulfilled/shipped/returned orders can post reviews.  
- **Templates & UI:** The product detail page renders the full feedback block (summary, form, and history). The `show` view seeds the form with the authenticated user’s nickname, disables duplicates on the client, and ensures only logged-in users can reach the feedback anchor.
- **Outcome:** Compared to `phase-4-5`, the branch adds a fully authenticated feedback lifecycle—sanitized inputs, duplicate prevention, verified‑purchase gating, and multi-layer rate limiting—while still surfacing aggregated scores for transparency. The changes keep the UI, model, and routing layers aligned to resist tampering even if a bandit-style static scan cannot reason about business intent.