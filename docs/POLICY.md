# Policy (Creative + Taste Constraints)

> **Doc type:** POLICY
> This file is the canonical source of truth for creative/taste constraints.

This document points to the **creative constraints** that shape what the system is allowed to produce.

Policy changes should not require controller rewrites. If a change requires new artifacts, gates, or parsing rules, it belongs in Mechanics.

## Core policy documents
- Stephanie taste profile (source of truth): `design/stephanie_taste_profile.md`
- Scope guardrails (what v1 will NOT do): `09_scope_boundaries.md`
- Trend firewall (how topics may inform ideas): `06_trend_rules.md`
- Character integrity bounds: `03_character_bible.md`

## Update rules
- Only explicit human statements update the taste profile.
- No learning from metrics, views, or silence.

## Red lines
The high-level red lines are also listed in `project.yaml` under `policy.red_lines` and should be enforced by Mabel + QC.
