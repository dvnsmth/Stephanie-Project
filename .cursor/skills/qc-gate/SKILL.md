---
name: qc-gate
description: Review rendered video/audio for technical defects and tone violations; output pass/fail with actionable fixes. Use when quality-checking a render before human review, or when the user asks for QC, technical review, or tone check on video/audio.
---

# QC Gate (Technical & Tone)

Review render output for technical defects and taste/tone violations before human review. QC does not block for subjective humor quality unless it violates explicit tone or safety rules.

## Non-Negotiables

- Do not rewrite the joke.
- Do not propose "trend fixes" or engagement hacks.
- Be explicit: **PASS** or **FAIL** with actionable fixes.

## Inputs

- Render report (version, runtime, VO/subs, prompt bundle summary)
- Optional: access to video/audio/subtitles
- Project principles and red lines

## Output Format

```markdown
## QC Result
- **Status:** PASS | FAIL
- **Version reviewed:** v__

## Findings
### Technical
- (e.g., audio clipping, unintelligible VO, visual artifacts, uncanny faces, text errors)

### Tone & Taste Risk
- (e.g., mean/performative drift, red-line violation)

### Structure
- (e.g., runtime within spec, standalone clarity)

## Required Fixes (if FAIL)
1. ...
2. ...

## Optional Improvements (if PASS)
- ...
```

## Checks

- **Technical:** Audio clarity, clipping; visual artifacts; text/subs errors; runtime within spec.
- **Tone:** Drift toward mean, performative, or red-line content.
- **Structure:** Standalone clarity; no dependency on missing context.

If any finding is **major** → FAIL and list required fixes. Do not approve and suggest "optional" fixes for major issues.
