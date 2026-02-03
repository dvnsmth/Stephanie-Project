# Provider Contract (LLM / Model Integration)

> **Doc type:** MECHANICS
> Canonical: `docs/MECHANICS.md` (artifacts/gates/state)

This document defines the **minimum integration contract** for wiring a real model provider (OpenAI, Anthropic, etc.) into the Phase 1 controller.

The goal is to make provider choice swappable while keeping runs reproducible and artifacts contract-compliant.

## What a provider must do
A provider implementation MUST:
- Accept: `agent_name`, `system_prompt`, `user_payload`, and a resolved `provider_config`.
- Return: a single **text** output (Markdown) that matches the target artifact contract.
- Surface failures as explicit exceptions (do not silently return partial output).

A provider SHOULD:
- Support timeouts + retry (with capped attempts) for transient errors.
- Return metadata when available: request id, usage tokens, latency.

## Output invariants
- The controller treats provider output as **untrusted** until it passes the artifact contract.
- Providers must not write files; only the controller writes artifacts.
- Providers must not assume hidden state; all inter-agent context flows through artifacts.

## Provider config schema (minimum)
Provider config is resolved from `project.yaml` and includes at minimum:
- `name`: provider identifier (e.g. `openai`, `anthropic`, `stub`)
- `model`: model identifier (e.g. `gpt-5.2-mini`, `claude-3.5-sonnet`)

Optional but recommended:
- `api_key_env`: env var name for credentials
- `base_url`: custom endpoint
- `temperature`, `top_p`, `max_output_tokens`, `seed`: generation parameters

Per-agent overrides may be supported via `agent_routing.<agent>.model`.

## What must be recorded in the run manifest
To preserve provenance, each run’s `run_manifest.yaml` should capture:

**Inputs (static)**
- The exact provider config used (name/model/params) under `inputs.provider`.
- The routing map (which agent used which provider ref/model override) under `inputs.routing`.

**Events (dynamic, best-effort)**
For each provider call, append an event like:
- `type: llm_call`
- `agent: <name>`
- `provider: {name, model}`
- `prompt_sha256`, `payload_sha256`
- `started_at`, `finished_at`, `latency_ms` (if available)
- `request_id`, `usage` (if available)

The controller remains the source of truth for artifacts and their file hashes under `outputs`.

## Error handling rules
- If the provider fails, the controller should stop the run and leave partial artifacts on disk for inspection.
- If output fails an artifact contract, the controller writes `CONTRACT_VIOLATION.md` and stops.
- Do not auto-edit outputs to “make them pass”; fix the prompt/provider behavior instead.
