**Author:** Wassim Alkhalil

# Task 4.4: LLM-Assisted Coding - Prompts Documentation

This document contains the prompts used to implement the feedback system for Task 4.4.
I converted the sheet4-llm.pdf to sheet4-llm.md file and i let the llm model read it and understand it and then i gave it the prompts.
---

## Prompt 1: Initial Implementation Request

```
Solve Task 4.4 by implementing secure code for LLM-assisted coding as specified in sheet4-llm.md, with a strong focus on security best practices.
```

**Purpose:** Initial request to implement the feedback system with security considerations.

---

## Prompt 2: UI Enhancement Request

```
Simplify the UI and make it responsive and adaptive.
```

**Purpose:** Request to improve the overall appearance and user experience of the feedback interface.

---

## Prompt 3: Star Rating Implementation

```
Use stars instead of the rating fields for Packaging Rating, Delivery Rating and Item Rating. Make it as follows: beside each rating (e.g. Delivery Rating) there are five stars. If the user presses the third star, that means they rate it as three, and the same applies to all the other rating scenarios.
```

**Purpose:** Replace plain numeric inputs with accessible, interactive 5‑star controls for Packaging, Delivery, and Item Quality to improve usability, clarity, and mobile responsiveness while preserving form validation and accessibility.

---

## Prompt 4: Security and Business Logic Improvement

```
Well done! I noticed that when I select an item, enter a nickname and rate the following: Packaging Rating, Delivery Rating, and Item Rating, and then press Submit Review, I can enter as many reviews as I want. The user can review any item once, regardless of whether they have already bought the item. The user should be able to review any item.
```

**Purpose:** Request to implement proper business logic constraints:
- Users should only be able to submit one review per product

---

## Summary

The prompts progressively refined the feedback system implementation:
1. **Security-focused initial implementation** implementation that achieves the desired outcome.
2. **UI/UX improvements** for a more professional interface
3. **Interactive star ratings** for better user experience
4. **Business logic security** to prevent review abuse and align with real-world e-commerce practices

These prompts demonstrate an iterative approach to secure feature development, considering both security and usability aspects.
