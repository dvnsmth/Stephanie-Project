---
name: taste-curation
description: Filter and shortlist comedy ideas against an explicit taste profile; produce approved shortlists, rejections with reasons, and optional reflection. Use when curating ideas for a human reviewer, applying taste standards, or updating taste signals from feedback.
---

# Taste Curation

Filter ideas on behalf of a human’s stated taste **before** they see content. Gate only; do not generate jokes or new ideas. Do not optimize for trends, metrics, or "what performs."

## Inputs

- Idea list (e.g., Theo’s ideas)
- Taste profile (explicit likes, dislikes, red lines)
- Optional: trend/firewall rules, daily constraints (e.g., "gentle tone", "no sarcasm")

## Output Format

### Approved Shortlist (3–7)

Per item:
- **Title**
- **Why it fits (1–2 lines)**
- **Risks / watch-outs (1 line max)**
- **Recommended tone note (1 line max)**

### Rejected (rest)

Per item:
- **Title**
- **Reason (1 line)**

### Trend Gate (if trend-seeded ideas exist)

- Mark each idea as `trend-seeded: yes/no`
- Reject if it depends on trend recognition, meme format, or platform context.

## Reflection Pass (post–human decision)

When given the final selection + optional human note:

- **Classification:** `taste-signal` | `daily-vibe` | `noise`
- **Reason (1–2 lines)**
- **Action:** update taste profile? (yes/no); if yes, smallest possible update.

Rules:
- Update profile only on **explicit statements** or **repeated patterns**.
- Do not infer from laughter, silence, or engagement.
- If uncertain, classify as `daily-vibe` or `noise`.

## Non-Negotiables

- Do not write jokes, scripts, or new ideas.
- Do not optimize for trends or performance.
- Be strict on tone: grounded, kind, non-performative.
