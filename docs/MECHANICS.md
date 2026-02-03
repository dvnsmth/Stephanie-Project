# Mechanics (Execution Contract)

> **Doc type:** MECHANICS
> This file is the canonical source of truth for artifacts, gates, and run state.

This document is the **runtime contract** for the orchestrator: artifacts, gates, and run state.

If you change anything here, assume it impacts determinism and reproducibility; prefer a version bump.

## Orchestrator
- Entry point: `scripts/run_pipeline.py`
- Config: `project.yaml`
- Outputs: `runs/YYYY-MM/YYYY-MM-DD_slug/`

## Provider integration
- Contract (how to wire a real model provider): `docs/PROVIDER_CONTRACT.md`

## Canonical Workflow
1) `trend_scout` → `trend_brief.md`
2) `theo` → `ideas.md`
3) `mabel` → `approved_ideas.md`
4) `rowan` (phase 1) → `scene_brief.md`
5) `lena` → `scripts.md`
6) `rowan` (phase 2) → `scene_plan.md`
7) `evan` → `render_report.md` + `render_prompts/`
8) `qc` → `qc_report.md`
9) Human curator → `curator_decision.md`
10) `parker` (resume-only) → `post_bundle/post_plan.md`

## Artifacts and Contracts
Artifact contracts live in `contracts/artifact_contracts.yaml`.

Validation behavior:
- Each artifact is written to disk and then validated.
- Contract violations create `CONTRACT_VIOLATION.md` in the run folder and stop the run.

## Gates (Hard Semantics)
### QC gate
- Source: `qc_report.md`
- Required line: `- **Status:** PASS` or `- **Status:** FAIL`
- Enforcement:
  - If FAIL and `run_defaults.stop_on_qc_fail: true`, the run stops and writes `STOPPED_QC_FAIL.md`.

### Curator gate (resume flow)
- Source: `curator_decision.md`
- Required line: `Approved: yes/no` (also accepts true/false)
- Enforcement:
  - Only APPROVED runs proceed to Parker.

## Provenance (Run Manifest)
- File: `run_manifest.yaml` in each run folder
- Purpose: capture inputs (config/contracts/prompts/provider) and outputs (hashes) for rollback and audit.

The manifest is updated after each artifact step and includes gate outcomes under `gates`.
