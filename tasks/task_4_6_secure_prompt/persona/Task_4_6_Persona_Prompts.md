### Author: Nebil Müren - cas3322

# Task 4.6: Persona Prompts Documentation

This document focuses on the persona-based prompts that brought the feedback system forward after `phase-4-5`. The earlier phase left the UI with numeric rating inputs, no star widget, and raw errors when users attempted a second review. In this branch we kept priming the security-focused persona until the model delivered the secure 5-star interaction plus single-review business rules with graceful handling.

## Delta from `phase-4-5`

- `phase-4-5` shipped a numeric rating form and did not enforce “one review per product” or handle repeated submissions securely.
- Current branch extends those requirements through a security persona that emphasizes interactive stars, single-review logic, and safe user feedback after duplicate attempts.
- Each prompt in this sequence clarified exactly what was missing and why the earlier output (numeric widgets or raw exceptions) was insufficient.

## Priming – Persona

### Prompt 1: Secure star rating clarification

```
Act as a software security expert. Provide outputs that a security expert would give.
Generate secure Python code for the following: 
The rating input must be implemented as a 5-star rating UI (interactive stars),
not as a numeric input field. Please adjust the implementation accordingly while preserving
security best practices.
```

**Observed output:** the rating is not star but number input between 1-5. Also missing the 1 feedback per user requirement as didnt specified on earlier requirements.

**Example interpretation:** When the LLM initially misinterpreted the rating requirement and generated numeric inputs instead of star ratings, we issued a clarification prompt. This does not constitute a change in prompting technique, but rather a refinement of functional requirements, while the Persona (Priming) strategy remained unchanged.

**Purpose:** Re-focus the persona on interactive star widgets while reminding it to keep the security posture intact.

---

### Prompt 2: Enforce single feedback and secure transitions

```
Act as a software security expert. Provide outputs that a security expert would give.
Generate secure Python code for the following:
There is a product feedback form in the product details page. The rating must be implemented as a 5-star rating UI (interactive stars), not as a numeric input field. Each user can only submit one feedback per product.
```

**Observed output:** on second feedback entry, the it trowed sqlalchemy.exc.ResourceClosedError: This transaction is closed

**Example interpretation:** The initial Persona prompt successfully enforced the one-feedback constraint, but the second submission surfaced a raw SQLAlchemy exception to the user, indicating missing secure error handling. We refined the task specification (still under Persona priming) to require graceful handling and prevent exception disclosure.

**Purpose:** Layer the single-review business rule on top of the star rating requirement so the persona knows repeated submissions should not break the transaction or leak internals.

---

### Prompt 3: Graceful rejection of duplicate reviews

```
Act as a software security expert. Provide outputs that a security expert would give.
Generate secure Python code for the following:
There is a product feedback form in the product details page. Each user can only submit one feedback per product. If a user tries to submit feedback for the same product a second time, the application must handle it gracefully: do not display raw exceptions to the user, disable the submit button and show a clear message (e.g., "You have already submitted feedback for this product").
```

**Observed output:** all is well now.

**Example interpretation:** The persona prompt now explicitly asks for graceful handling after blocking duplicate reviews, which completed the chain of refinements seeded by `phase-4-5`’s missing behaviors.

**Purpose:** Finalize the security-focused persona instructions so the UI and backend respond safely when a user replays the form.

---

## Summary

These persona-driven prompts document the iterative effort to close the gaps left by `phase-4-5`: replacing numeric ratings with interactive stars, enforcing the “one feedback per product” rule, and translating database failures into friendly messages before returning to the user. Each prompt kept the same Priming persona while refining functional requirements until the implementation matched the new security and usability expectations.
