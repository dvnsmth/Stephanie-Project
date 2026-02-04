# README — Orchestrator Scaffold (Phase 1)

This scaffold runs the pipeline end-to-end **in stub mode**:
it writes artifacts to disk and produces a render prompt bundle
without calling any external LLM APIs yet.

## What you get now
- A runnable controller: `scripts/run_pipeline.py`
- Standard run folder + artifacts
- Agent prompt files under `agents/`
- Design docs under `design/`

## Canonical docs
- Execution contract (artifacts/gates/state): `docs/MECHANICS.md`
- Creative constraints (taste/scope/trends): `docs/POLICY.md`

## Status (planning hardening)
- Artifact contracts + validator: complete
- `scene_brief` → `scripts` → `scene_plan` workflow: complete
- Run provenance (`run_manifest.yaml`): complete
- Gate semantics (QC + curator resume): complete
- Policy vs mechanics doc split: complete
- Provider integration contract + abstraction: complete

## Next step to make it real
Implement one provider client (Claude SDK, OpenAI Responses, etc.) following `docs/PROVIDER_CONTRACT.md`,
then replace `StubProvider` in `scripts/provider.py` (or introduce a real Provider implementation and use it in `scripts/run_pipeline.py`).

## Quickstart
```bash
python scripts/run_pipeline.py --config project.yaml --date 2026-02-02 --slug test_run
```

This will create:
`runs/2026-02/2026-02-02_test_run/` with:
- trend_brief.md
- ideas.md
- approved_ideas.md
- scene_brief.md
- scripts.md
- scene_plan.md
- render_report.md
- render_prompts/*
- qc_report.md
- run_manifest.yaml
- READY_FOR_CURATOR.md
- curator_decision.md (template copy)

Then:
1) Copy `templates/curator_decision.template.md` into the run folder as `curator_decision.md`
2) Fill it out (Approved yes/no)
3) Re-run:
```bash
python scripts/run_pipeline.py --config project.yaml --resume runs/2026-02/2026-02-02_test_run
```
If approved=yes, Parker will generate the post bundle.
