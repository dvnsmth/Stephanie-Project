"""Artifact contract loading + validation.

Contracts are intentionally minimal: they enforce required headings/markers to prevent drift.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ContractResult:
    ok: bool
    message: str


def load_contracts(contracts_path: Path) -> dict[str, Any]:
    if not contracts_path.exists():
        raise FileNotFoundError(f"Missing contracts file: {contracts_path}")
    data = yaml.safe_load(contracts_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "artifacts" not in data:
        raise ValueError("Invalid contracts file: expected top-level 'artifacts'")
    return data


def validate_artifact(contracts: dict[str, Any], artifact_key: str, content: str) -> ContractResult:
    artifacts = contracts.get("artifacts", {})
    contract = artifacts.get(artifact_key)
    if contract is None:
        return ContractResult(ok=True, message=f"No contract for artifact '{artifact_key}' (skipping).")

    required_headings = contract.get("required_headings") or []
    for heading in required_headings:
        if heading not in content:
            return ContractResult(ok=False, message=f"Missing required heading: {heading}")

    required_any = contract.get("required_any") or []
    if required_any:
        if not any(marker in content for marker in required_any):
            return ContractResult(
                ok=False,
                message=f"Missing required marker (any of): {', '.join(required_any)}",
            )

    required_yaml_keys = contract.get("required_yaml_keys") or []
    if required_yaml_keys:
        try:
            parsed = yaml.safe_load(content)
        except Exception as e:
            return ContractResult(ok=False, message=f"Invalid YAML: {e}")

        if not isinstance(parsed, dict):
            return ContractResult(ok=False, message="Invalid YAML: expected mapping at root")

        for key_path in required_yaml_keys:
            if not _has_key_path(parsed, key_path):
                return ContractResult(ok=False, message=f"Missing required YAML key: {key_path}")

    return ContractResult(ok=True, message="OK")


def _has_key_path(root: dict[str, Any], key_path: str) -> bool:
    """Check a dotted key path like 'inputs.config.sha256'."""
    cur: Any = root
    for part in key_path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return False
        cur = cur[part]
    return True
