### Author: Nebil Müren - cas3322

# Task 4.6: Persona Justification

## Where the code looks good

- **Frontend feedback inputs are now read-only and consistent**  
  - The rating fields are hidden integers synchronized with interactive 5-star controls. The client script never writes user input directly to the DOM; it simply toggles the star states, fills the hidden inputs, and keeps the values in range.
  - The updated CSS/JS bundle is the only place that deals with those controls, so the numeric data that reaches Flask is predictable (1-5) and still validated with `NumberRange`.

- **Server side resists duplicate submissions**  
  - `ProductFeedback` now carries `user_id` plus a `(product_id, user_id)` uniqueness constraint, so the database enforces “one feedback per user per product” even if a malicious client bypasses the UI checks.
  - The view queries for an existing record, flashes a clear warning if the user tries to re-submit, and never lets duplicate rows reach the ORM.

- **Existing feedback is shown/locked gracefully**  
  - When feedback exists, we pre-load the hidden rating inputs and disable the stars/submit button in the template while still showing the stored comment, so users can read their previous response without triggering an error.

***

## Bandit report (bandit-results-4-6-3.html)

- Total LOC flagged by the latest scan: 7,546 with 20 lines skipped for `#nosec`.
- No candidate issues or vulnerabilities were reported at all, which makes sense because the new code still confines itself to ORM operations, sanitized form data, and expressively controlled frontend behavior.
- The static analysis adds no new concerns, so the human review should focus on the application-level protections (rate limiting, configuration of Redis, etc.) instead of low-level code smells.

***

## Delta vs. phase-4-5

- Forms & views: `ProductFeedbackForm` now keeps the rating widgets hidden and pre-loaded, while `product_feedback` short-circuits duplicate inserts with a `flash` instead of general exception handling. The `show` view reuses cached feedback to seed the UI and reports `already_submitted` so the template can disable further input.
- Models & schema: `ProductFeedback` gained `user_id` plus a unique constraint, meaning the database enforces the “one feedback per product per user” invariant even if someone bypasses the UI or CSRF protections.
- Templates & assets: The product detail page now renders three star groups tied to hidden inputs, and the static CSS/JS bundles received the styles and client-side behavior to highlight stars, respect `data-rating-disabled`, and keep the ARIA values in sync.
- Outcome: Compared to `phase-4-5`, this branch hardens both the UX and the persistence layer—repeated submissions are detected early, the user receives a friendly message instead of raw errors, and the star rating UI is the only Surface where the rating values can be set, minimizing the attack surface for tampered inputs.