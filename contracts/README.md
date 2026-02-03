# Contracts

This folder defines **artifact contracts**: lightweight rules that keep agent outputs stable, parseable, and resistant to drift.

## Why contracts exist
- Agents collaborate via files, not chatter.
- Markdown is flexible, so outputs can silently change shape.
- Contracts create a minimal shared structure that downstream steps can rely on.

## What is enforced (v1)
Contracts are intentionally minimal:
- Required headings (and a few required markers)
- No deep parsing

The controller validates artifacts after each step and can stop early if a contract is violated.

## Files
- `artifact_contracts.yaml`: required headings per artifact key.
