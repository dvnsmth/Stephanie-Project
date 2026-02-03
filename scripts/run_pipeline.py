#!/usr/bin/env python3
"""run_pipeline.py — The Stephanie Project (Phase 1 Controller)

Phase 1 is intentionally provider-agnostic and runs in STUB mode by default.
Replace `call_llm()` with your chosen provider client (Claude SDK / OpenAI Responses / etc.).
"""

import argparse
import datetime as dt
import os
import time
from pathlib import Path
import yaml
import shutil

try:
    # When executed as a module: python -m scripts.run_pipeline
    from scripts.artifact_contracts import load_contracts, validate_artifact
    from scripts.provenance import sha256_file, sha256_text
    from scripts.gates import parse_curator_approval, parse_qc_status
    from scripts.provider import Provider, StubProvider, resolve_provider_config
except ImportError:
    # When executed as a script: python scripts/run_pipeline.py
    from artifact_contracts import load_contracts, validate_artifact
    from provenance import sha256_file, sha256_text
    from gates import parse_curator_approval, parse_qc_status
    from provider import Provider, StubProvider, resolve_provider_config

# ---------------------------
# Utilities
# ---------------------------

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

def now_iso() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")

def _rel_path(root_dir: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root_dir)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")

def load_config(config_path: Path) -> dict:
    return yaml.safe_load(read_text(config_path))

def ensure_run_dir(runs_dir: Path, date: str, slug: str) -> Path:
    # runs/YYYY-MM/YYYY-MM-DD_slug/
    yyyy_mm = date[:7]
    run_dir = runs_dir / yyyy_mm / f"{date}_{slug}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir

def copy_template(src: Path, dst: Path) -> None:
    if not dst.exists():
        shutil.copyfile(src, dst)

def build_policy_manifest(root_dir: Path, policy_cfg: dict | None) -> dict:
    policy_manifest: dict[str, dict] = {}
    for key, rel in (policy_cfg or {}).items():
        if key == "red_lines":
            continue
        if not isinstance(rel, str):
            continue
        policy_path = (root_dir / rel).resolve() if not Path(rel).is_absolute() else Path(rel)
        policy_manifest[key] = {
            "path": _rel_path(root_dir, policy_path),
            "sha256": sha256_file(policy_path) if policy_path.exists() else None,
        }
    return policy_manifest

def set_run_state(manifest: dict, state: str, *, reason: str | None = None) -> None:
    run = manifest.setdefault("run", {})
    history = run.setdefault("state_history", [])
    if run.get("state") == state:
        return
    run["state"] = state
    history.append({"state": state, "at": now_iso(), "reason": reason})


def stub_output(agent_name: str, user_payload: str) -> str:
    """Return contract-compliant stub outputs per agent.

    This keeps Phase 1 runs deterministic and parseable even before a provider is wired.
    """

    if agent_name == "trend_scout":
        return (
            "## Trend Brief\n"
            "- **Window:** last 72 hours\n"
            "- **Region:** US\n"
            "- **Sources:** (stub)\n\n"
            "## Topics (5–10)\n"
            "- **Topic:** bedtime logistics\n"
            "  - **Context (1–2 sentences):** Parents coordinating routines across ages.\n"
            "  - **Stability:** evergreen-adjacent\n"
            "  - **Human angle (1 sentence):** Everyone is trying to be helpful at once.\n"
            "  - **Risk flags:** none\n"
        )

    if agent_name == "theo":
        return (
            "## Ideas\n"
            "1. **Title:** The Lunchbox That Won’t Close\n"
            "   - **Premise (1–2 sentences):** A parent calmly tries to pack an overstuffed lunchbox while pretending it’s fine.\n"
            "   - **Pressure source:** situational\n"
            "   - **Release mechanism:** deflation\n"
            "   - **Core contrast:** prepared vs reality\n"
            "   - **Tension pattern:**\n"
            "     - repeated action → interruption\n"
            "   - **Tag:** `sketch`\n"
            "   - **Tone:** warm\n"
        )

    if agent_name == "mabel":
        return (
            "## Approved Shortlist (3–7)\n"
            "- **Title:** The Lunchbox That Won’t Close\n"
            "- **Why it fits (1–2 lines):** Domestic, relatable, kind; no mean edge.\n"
            "- **Risks / watch-outs (1 line max):** Avoid frantic energy.\n"
            "- **Recommended tone note (1 line max):** Calm, understated.\n\n"
            "## Selection Notes\n"
            "- **Shortlist rationale (1–2 lines):** Strong domestic fit; minimal risk.\n"
            "- **Global cautions (1 line):** Keep pacing calm; avoid escalation.\n\n"
            "## Rejected (rest)\n"
            "- **Title:** (stub rejected idea)\n"
            "- **Reason (1 line):** Too performative for the tone rules.\n"
        )

    if agent_name == "lena":
        return (
            "## The Lunchbox That Won’t Close\n\n"
            "### Source Brief\n"
            "- **Scene brief title:** The Lunchbox That Won’t Close\n"
            "- **Dialogue budget honored:** yes\n\n"
            "### Dialogue (spoken) — if any\n"
            "- Alex: It’s fine. It’s… a design feature.\n"
            "- Riley: The zipper is crying.\n"
            "- Alex: We don’t talk about that.\n\n"
            "### Silent / Visual Beats (2–5 bullets)\n"
            "- A calm attempt to close the lunchbox.\n"
            "- A quiet pause.\n"
            "- The lunchbox gently pops open again.\n\n"
            "### Alt Punchlines (optional, 0–3)\n"
            "- Alex: I’m just giving it room to breathe.\n\n"
            "### Subtitle Text (if spoken)\n"
            "It’s fine. It’s… a design feature.\n"
            "The zipper is crying.\n"
            "We don’t talk about that.\n\n"
            "### Notes\n"
            "- Recommend silence? no\n"
            "- Any delivery cautions: keep it understated\n"
        )

    if agent_name == "rowan":
        wants_brief = "OUTPUT: scene_brief" in user_payload
        if wants_brief:
            return (
                "# scene_brief.md\n\n"
                "## Title\n"
                "The Lunchbox That Won’t Close\n\n"
                "## Source Idea\n"
                "The Lunchbox That Won’t Close\n\n"
                "## Scene Intent\n"
                "A calm attempt to handle a tiny morning problem without making it a big thing.\n\n"
                "## Characters Present\n"
                "- Alex:\n"
                "  - Role in scene: parent/guardian packing\n"
                "  - Emotional state entering: calm, tired, determined\n"
                "  - Integrity bounds: no performative meltdown\n"
                "- Riley:\n"
                "  - Role in scene: helpful second adult\n"
                "  - Emotional state entering: warm, lightly amused\n"
                "  - Integrity bounds: never mean\n\n"
                "## Selection Notes\n"
                "Chosen for domestic realism and gentle tension with a clean release.\n\n"
                "## Tension Pattern\n"
                "repeated action → interruption\n\n"
                "## Pressure Source\n"
                "situational\n\n"
                "## Release Target\n"
                "Expected: zipper closes if you try harder. Actual: it simply won’t, and the calm acceptance is the release.\n\n"
                "## Dialogue Budget\n"
                "- Total spoken lines: 0–3\n"
                "- Preferred speakers: Alex (primary), Riley (optional)\n"
                "- Silence encouraged? yes\n\n"
                "## Notes for Lena\n"
                "- Tone reminders: understated, warm\n"
                "- What the line must accomplish (not wording): name the denial/acceptance without explaining the joke\n\n"
                "## Notes for Rowan\n"
                "- Required beats: pack → zip attempt → pop-open → calm reaction → end\n"
                "- Visual storytelling allowed: yes (minimal)\n"
                "- Runtime target (seconds): 25\n"
            )

        return (
            "## The Lunchbox That Won’t Close\n"
            "### Source References\n"
            "- **Scene brief title:** The Lunchbox That Won’t Close\n"
            "- **Script title:** The Lunchbox That Won’t Close\n\n"
            "### Mode\n"
            "- `sketch`\n\n"
            "### Beat Sheet (3–7 beats)\n"
            "1. Alex packs calmly; the lunchbox is clearly overfull.\n"
            "2. Alex tries to zip it with quiet determination.\n"
            "3. Riley notices and offers gentle help.\n"
            "4. The lunchbox pops open; Alex stays composed.\n"
            "5. Minimal release line (or silence); scene ends cleanly.\n\n"
            "### Character Placement\n"
            "- On-screen: Alex, Riley\n"
            "- Off-screen / implied: kid presence implied via lunchbox\n"
            "- Integrity notes (1–2 lines): Keep reactions calm; no mockery.\n\n"
            "### Environment & Props (minimal)\n"
            "- Location: kitchen counter\n"
            "- Key props: lunchbox, snacks\n"
            "- Wardrobe/continuity notes (if needed): casual morning clothes\n\n"
            "### Shot Plan (simple, no film jargon beyond shot size)\n"
            "- Shot 1: medium — packing — 6s\n"
            "- Shot 2: close — zipper resisting — 6s\n"
            "- Shot 3: medium — pop open + reaction — 8s\n\n"
            "### Dialogue Slots (if any)\n"
            "- **Speaker:** Alex\n"
            "  - **Function:** release\n"
            "  - **Constraint:** calm, minimal words\n"
            "  - **Timing:** release\n\n"
            "### Render Notes (for realism)\n"
            "- Lighting mood: morning natural\n"
            "- Movement level: low\n"
            "- Avoid:\n"
            "  - exaggerated expressions\n"
            "  - cartoonish motion\n"
            "  - dramatic fantasy styling\n\n"
            "### Continuity Check\n"
            "- Any risk of escalation or repetition? (yes/no + 1 line) no\n"
            "- Does it work without prior context? (yes/no) yes\n"
        )

    if agent_name == "evan":
        return (
            "## Render Output\n"
            "- **Version:** v1\n"
            "- **Runtime:** 25 seconds\n"
            "- **VO:** yes\n"
            "- **Subtitles:** no\n\n"
            "## Source Inputs\n"
            "- **scene_plan.md:** The Lunchbox That Won’t Close\n"
            "- **scripts.md:** The Lunchbox That Won’t Close\n"
            "- **prompt bundle path:** render_prompts/v1/\n\n"
            "## Prompt Bundle Summary\n"
            "- Shot count: 3\n"
            "- Key continuity locks: kitchen lighting; lunchbox color; wardrobe neutral\n"
            "- Any fixes applied since last version: none (stub)\n\n"
            "## QC Self-Check (before handoff)\n"
            "- Visual artifacts: none\n"
            "- Audio clarity: good\n"
            "- Tone drift risk: none\n"
            "- Standalone clarity: yes\n"
        )

    if agent_name == "qc":
        return (
            "## QC Result\n"
            "- **Status:** PASS\n"
            "- **Version reviewed:** v1\n\n"
            "## Findings\n"
            "### Technical\n"
            "- (stub) No issues found.\n\n"
            "### Tone & Taste Risk\n"
            "- (stub) No violations.\n\n"
            "### Structure\n"
            "- (stub) One clean comedic turn; ends cleanly.\n\n"
            "## Optional Improvements (if PASS)\n"
            "- (stub) Consider a slightly longer pause before the pop-open.\n"
        )

    if agent_name == "parker":
        return (
            "## Post Bundle\n"
            "- **Assets:**\n"
            "  - final video: final.mp4\n"
            "  - variants (if any): none\n"
            "  - subtitles (if any): none\n\n"
            "## Captions (1–3)\n"
            "1. Morning wins are still wins.\n\n"
            "## Upload Notes\n"
            "- Any required crops: none\n"
            "- Subtitle toggle: off\n"
            "- Hashtags: none\n\n"
            "## Final Gate\n"
            "- Confirm: Stephanie approved (yes/no) yes\n"
        )

    return "(stub)"

# ---------------------------
# STUB LLM call (replace later)
# ---------------------------

def _resolve_agent_provider_cfg(cfg: dict, agent_name: str):
    route = (cfg.get("agent_routing") or {}).get(agent_name, {})
    provider_ref = route.get("provider") or "default"
    provider_raw = (cfg.get("providers") or {}).get(provider_ref, {})
    model_override = route.get("model")
    return provider_ref, resolve_provider_config(provider_raw, model_override=model_override)


def _record_llm_call_event(
    manifest: dict,
    *,
    agent_name: str,
    provider_name: str,
    model: str,
    system_prompt: str,
    user_payload: str,
    started_at: str,
    finished_at: str,
    latency_ms: int,
    request_id: str | None,
    usage: dict | None,
) -> None:
    manifest.setdefault("events", []).append(
        {
            "type": "llm_call",
            "agent": agent_name,
            "provider": {"name": provider_name, "model": model},
            "prompt_sha256": sha256_text(system_prompt),
            "payload_sha256": sha256_text(user_payload),
            "started_at": started_at,
            "finished_at": finished_at,
            "latency_ms": latency_ms,
            "request_id": request_id,
            "usage": usage,
        }
    )


def call_llm(
    *,
    cfg: dict,
    provider: Provider,
    agent_name: str,
    system_prompt: str,
    user_payload: str,
    manifest: dict | None = None,
) -> str:
    """Provider-agnostic call.

    In Phase 1 this uses StubProvider, but the interface is the same for real providers.
    """
    _, provider_cfg = _resolve_agent_provider_cfg(cfg, agent_name)
    started_at = now_iso()
    t0 = time.perf_counter()
    result = provider.generate(
        agent_name=agent_name,
        system_prompt=system_prompt,
        user_payload=user_payload,
        config=provider_cfg,
    )
    latency_ms = int((time.perf_counter() - t0) * 1000)
    finished_at = now_iso()

    if manifest is not None:
        _record_llm_call_event(
            manifest,
            agent_name=agent_name,
            provider_name=result.provider_name,
            model=result.model,
            system_prompt=system_prompt,
            user_payload=user_payload,
            started_at=started_at,
            finished_at=finished_at,
            latency_ms=latency_ms,
            request_id=getattr(result, "request_id", None),
            usage=getattr(result, "usage", None),
        )
    return result.text


def validate_and_write(
    *,
    contracts: dict,
    artifact_key: str,
    out_path: Path,
    content: str,
) -> None:
    """Write artifact, then validate it against the contract.

    Writing first ensures you can inspect the violating output.
    """
    write_text(out_path, content)
    result = validate_artifact(contracts, artifact_key, content)
    if not result.ok:
        violation_path = out_path.parent / "CONTRACT_VIOLATION.md"
        write_text(
            violation_path,
            (
                "# CONTRACT_VIOLATION\n\n"
                f"Artifact: {artifact_key}\n\n"
                f"Path: {out_path.name}\n\n"
                f"Reason: {result.message}\n"
            ),
        )
        raise ValueError(f"Artifact contract failed for '{artifact_key}': {result.message}")


def upsert_output_manifest(manifest: dict, artifact_key: str, out_path: Path) -> None:
    """Record output file metadata in the run manifest."""
    if not out_path.exists():
        return
    rel = out_path.name
    manifest.setdefault("outputs", {})[artifact_key] = {
        "path": rel,
        "sha256": sha256_file(out_path),
        "bytes": out_path.stat().st_size,
        "updated_at": now_iso(),
    }


def record_gate(manifest: dict, gate_name: str, decision: str, *, source: str | None = None) -> None:
    manifest.setdefault("gates", {})[gate_name] = {
        "decision": decision,
        "at": now_iso(),
        "source": source,
    }

# ---------------------------
# Pipeline steps
# ---------------------------

def load_agent_prompt(agents_dir: Path, prompt_file: str) -> str:
    p = agents_dir / prompt_file
    if not p.exists():
        raise FileNotFoundError(f"Missing agent prompt file: {p}")
    return read_text(p)

def step_trend_scout(cfg: dict, run_dir: Path, agents_dir: Path, contracts: dict, provider: Provider, manifest: dict) -> Path:
    prompt = load_agent_prompt(agents_dir, cfg['agent_routing']['trend_scout']['prompt_file'])
    payload = "Window: last 72 hours\nRegion: US\n"
    out = call_llm(cfg=cfg, provider=provider, agent_name="trend_scout", system_prompt=prompt, user_payload=payload, manifest=manifest)
    out_path = run_dir / cfg['artifacts']['trend_brief']
    validate_and_write(contracts=contracts, artifact_key="trend_brief", out_path=out_path, content=out)
    return out_path

def step_theo(cfg: dict, run_dir: Path, agents_dir: Path, contracts: dict, provider: Provider, manifest: dict, trend_brief_path: Path) -> Path:
    prompt = load_agent_prompt(agents_dir, cfg['agent_routing']['theo']['prompt_file'])
    payload = (
        f"Batch size: {cfg['run_defaults']['batch_size_ideas']}\n\n"
        "--- trend_brief.md ---\n"
        f"{read_text(trend_brief_path)}\n"
    )
    out = call_llm(cfg=cfg, provider=provider, agent_name="theo", system_prompt=prompt, user_payload=payload, manifest=manifest)
    out_path = run_dir / cfg['artifacts']['ideas']
    validate_and_write(contracts=contracts, artifact_key="ideas", out_path=out_path, content=out)
    return out_path

def step_mabel(cfg: dict, run_dir: Path, agents_dir: Path, contracts: dict, provider: Provider, manifest: dict, ideas_path: Path) -> Path:
    prompt = load_agent_prompt(agents_dir, cfg['agent_routing']['mabel']['prompt_file'])
    taste_path = Path(cfg['policy']['stephanie_taste_profile'])
    payload = (
        "--- stephanie_taste_profile.md ---\n"
        f"{read_text(taste_path)}\n\n"
        "--- ideas.md ---\n"
        f"{read_text(ideas_path)}\n"
    )
    out = call_llm(cfg=cfg, provider=provider, agent_name="mabel", system_prompt=prompt, user_payload=payload, manifest=manifest)
    out_path = run_dir / cfg['artifacts']['approved_ideas']
    validate_and_write(contracts=contracts, artifact_key="approved_ideas", out_path=out_path, content=out)
    return out_path

def step_rowan_scene_brief(cfg: dict, run_dir: Path, agents_dir: Path, contracts: dict, provider: Provider, manifest: dict, approved_ideas_path: Path) -> Path:
    prompt = load_agent_prompt(agents_dir, cfg['agent_routing']['rowan']['prompt_file'])
    character_bible = Path(cfg['policy']['character_bible'])
    payload = (
        "OUTPUT: scene_brief\n"
        "Select the first item in the approved shortlist and produce a single scene_brief.md.\n\n"
        "--- character_bible.md ---\n"
        f"{read_text(character_bible)}\n\n"
        "--- approved_ideas.md ---\n"
        f"{read_text(approved_ideas_path)}\n"
    )
    out = call_llm(cfg=cfg, provider=provider, agent_name="rowan", system_prompt=prompt, user_payload=payload, manifest=manifest)
    out_path = run_dir / cfg['artifacts']['scene_brief']
    validate_and_write(contracts=contracts, artifact_key="scene_brief", out_path=out_path, content=out)
    return out_path


def step_lena(cfg: dict, run_dir: Path, agents_dir: Path, contracts: dict, provider: Provider, manifest: dict, scene_brief_path: Path) -> Path:
    prompt = load_agent_prompt(agents_dir, cfg['agent_routing']['lena']['prompt_file'])
    character_bible = Path(cfg['policy']['character_bible'])
    payload = (
        f"Target length: {cfg['run_defaults']['target_seconds']} seconds\n\n"
        "--- character_bible.md ---\n"
        f"{read_text(character_bible)}\n\n"
        "--- scene_brief.md ---\n"
        f"{read_text(scene_brief_path)}\n"
    )
    out = call_llm(cfg=cfg, provider=provider, agent_name="lena", system_prompt=prompt, user_payload=payload, manifest=manifest)
    out_path = run_dir / cfg['artifacts']['scripts']
    validate_and_write(contracts=contracts, artifact_key="scripts", out_path=out_path, content=out)
    return out_path

def step_rowan_scene_plan(
    cfg: dict,
    run_dir: Path,
    agents_dir: Path,
    contracts: dict,
    provider: Provider,
    manifest: dict,
    scene_brief_path: Path,
    scripts_path: Path,
) -> Path:
    prompt = load_agent_prompt(agents_dir, cfg['agent_routing']['rowan']['prompt_file'])
    character_bible = Path(cfg['policy']['character_bible'])
    payload = (
        "OUTPUT: scene_plan\n"
        "--- character_bible.md ---\n"
        f"{read_text(character_bible)}\n\n"
        "--- scene_brief.md ---\n"
        f"{read_text(scene_brief_path)}\n\n"
        "--- scripts.md ---\n"
        f"{read_text(scripts_path)}\n"
    )
    out = call_llm(cfg=cfg, provider=provider, agent_name="rowan", system_prompt=prompt, user_payload=payload, manifest=manifest)
    out_path = run_dir / cfg['artifacts']['scene_plan']
    validate_and_write(contracts=contracts, artifact_key="scene_plan", out_path=out_path, content=out)
    return out_path

def step_evan(cfg: dict, run_dir: Path, agents_dir: Path, contracts: dict, provider: Provider, manifest: dict, scene_plan_path: Path, scripts_path: Path) -> Path:
    """Evan produces render prompt bundles + report (stubbed)."""
    prompt = load_agent_prompt(agents_dir, cfg['agent_routing']['evan']['prompt_file'])
    payload = (
        f"Aspect ratio: {cfg['run_defaults']['aspect_ratio']}\n"
        f"Resolution: {cfg['run_defaults']['resolution']}\n"
        f"Target seconds: {cfg['run_defaults']['target_seconds']}\n\n"
        "--- scene_plan.md ---\n"
        f"{read_text(scene_plan_path)}\n\n"
        "--- scripts.md ---\n"
        f"{read_text(scripts_path)}\n"
    )
    out = call_llm(cfg=cfg, provider=provider, agent_name="evan", system_prompt=prompt, user_payload=payload, manifest=manifest)

    # Create prompt bundle folder
    bundle = run_dir / "render_prompts" / "v1"
    bundle.mkdir(parents=True, exist_ok=True)
    write_text(bundle / "shot_01.txt", "(stub) shot prompt goes here\n")
    write_text(bundle / "voice.txt", "(stub) voice prompt goes here\n")
    write_text(bundle / "edit_notes.md", "(stub) edit/assembly notes\n")
    report_path = run_dir / cfg['artifacts'].get('render_report', 'render_report.md')
    validate_and_write(contracts=contracts, artifact_key="render_report", out_path=report_path, content=out)
    return report_path

def step_qc(cfg: dict, run_dir: Path, agents_dir: Path, contracts: dict, provider: Provider, manifest: dict, render_report_path: Path) -> Path:
    prompt = load_agent_prompt(agents_dir, cfg['agent_routing']['qc']['prompt_file'])
    payload = (
        "--- render_report.md ---\n"
        f"{read_text(render_report_path)}\n"
    )
    out = call_llm(cfg=cfg, provider=provider, agent_name="qc", system_prompt=prompt, user_payload=payload, manifest=manifest)
    out_path = run_dir / cfg['artifacts']['qc_report']
    validate_and_write(contracts=contracts, artifact_key="qc_report", out_path=out_path, content=out)
    return out_path

def mark_ready_for_curator(run_dir: Path) -> None:
    write_text(run_dir / "READY_FOR_CURATOR.md",
               "# READY_FOR_CURATOR\n\nAll artifacts generated. Add curator_decision.md to proceed.\n")

def step_parker(cfg: dict, run_dir: Path, agents_dir: Path, curator_decision_path: Path, provider: Provider, manifest: dict) -> Path:
    prompt = load_agent_prompt(agents_dir, cfg['agent_routing']['parker']['prompt_file'])
    payload = read_text(curator_decision_path)
    out = call_llm(cfg=cfg, provider=provider, agent_name="parker", system_prompt=prompt, user_payload=payload, manifest=manifest)

    post_bundle = run_dir / "post_bundle"
    post_bundle.mkdir(parents=True, exist_ok=True)
    write_text(post_bundle / "post_plan.md", out)
    return post_bundle / "post_plan.md"

# ---------------------------
# Main
# ---------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="project.yaml", help="Path to project.yaml")
    ap.add_argument("--date", default=None, help="YYYY-MM-DD (defaults to today)")
    ap.add_argument("--slug", default="run", help="Run slug (e.g., test_run)")
    ap.add_argument("--resume", default=None, help="Path to existing run folder to resume after curator decision")
    args = ap.parse_args()

    cfg = load_config(Path(args.config))
    root_dir = Path(__file__).resolve().parents[1]
    agents_dir = root_dir / cfg['paths']['agents_dir']
    runs_dir = root_dir / cfg['paths']['runs_dir']
    templates_dir = root_dir / cfg['paths']['templates_dir']

    contracts_path = root_dir / "contracts" / "artifact_contracts.yaml"
    contracts = load_contracts(contracts_path)

    # Initialize run manifest (written into each run folder)
    cfg_path = Path(args.config)
    cfg_abs = (root_dir / cfg_path).resolve() if not cfg_path.is_absolute() else cfg_path
    contracts_abs = contracts_path.resolve()

    prompts_manifest = {}
    for agent_name, route in cfg.get("agent_routing", {}).items():
        prompt_rel = route.get("prompt_file")
        if not prompt_rel:
            continue
        prompt_path = (agents_dir / prompt_rel).resolve()
        if prompt_path.exists():
            prompts_manifest[agent_name] = {
                "path": _rel_path(root_dir, prompt_path),
                "sha256": sha256_file(prompt_path),
            }
        else:
            prompts_manifest[agent_name] = {
                "path": _rel_path(root_dir, prompt_path),
                "sha256": None,
            }

    policy_manifest = build_policy_manifest(root_dir, cfg.get("policy", {}))

    # Ensure taste profile exists
    taste_path = root_dir / cfg['policy']['stephanie_taste_profile']
    taste_path.parent.mkdir(parents=True, exist_ok=True)
    if not taste_path.exists():
        write_text(taste_path, "# stephanie_taste_profile.md\n\n(fill in)\n")

    # Resume path flow (after curator decision)
    if args.resume:
        run_dir = Path(args.resume)
        manifest_path = run_dir / cfg['artifacts'].get('run_manifest', 'run_manifest.yaml')
        provider = StubProvider(stub_output)
        manifest = {
            "schema_version": "v1",
            "run": {
                "id": run_dir.name,
                "created_at": now_iso(),
                "mode": "resume",
            },
            "inputs": {
                "config": {
                    "path": _rel_path(root_dir, cfg_abs),
                    "sha256": sha256_file(cfg_abs) if cfg_abs.exists() else None,
                },
                "contracts": {
                    "path": _rel_path(root_dir, contracts_abs),
                    "sha256": sha256_file(contracts_abs),
                },
                "prompts": prompts_manifest,
                "policy": policy_manifest,
                "provider": cfg.get("providers", {}).get("default", {}),
                "routing": {
                    agent: {
                        "provider": (route or {}).get("provider"),
                        "model": (route or {}).get("model"),
                        "prompt_file": (route or {}).get("prompt_file"),
                    }
                    for agent, route in (cfg.get("agent_routing", {}) or {}).items()
                },
            },
            "outputs": {},
            "events": [
                {
                    "type": "resume",
                    "at": now_iso(),
                }
            ],
        }

        # If an existing manifest is present, preserve it and append event.
        if manifest_path.exists():
            try:
                existing = yaml.safe_load(read_text(manifest_path))
                if isinstance(existing, dict):
                    existing.setdefault("events", []).append({"type": "resume", "at": now_iso()})
                    existing.setdefault("inputs", {}).setdefault(
                        "provider", cfg.get("providers", {}).get("default", {})
                    )
                    existing.setdefault("inputs", {}).setdefault(
                        "policy", policy_manifest
                    )
                    existing.setdefault("inputs", {}).setdefault(
                        "routing",
                        {
                            agent: {
                                "provider": (route or {}).get("provider"),
                                "model": (route or {}).get("model"),
                                "prompt_file": (route or {}).get("prompt_file"),
                            }
                            for agent, route in (cfg.get("agent_routing", {}) or {}).items()
                        },
                    )
                    manifest = existing
            except Exception:
                pass

        set_run_state(manifest, "READY_FOR_CURATOR", reason="resume")

        curator_path = run_dir / cfg['artifacts']['curator_decision']
        if not curator_path.exists():
            raise FileNotFoundError(f"Missing curator_decision.md in {run_dir}")
        curator_text = read_text(curator_path)
        curator_decision = parse_curator_approval(curator_text)
        record_gate(manifest, "curator", curator_decision.status, source=curator_path.name)
        if curator_decision.status != "APPROVED":
            set_run_state(manifest, "CURATOR_VETOED", reason="curator_decision")
            print("Curator vetoed / not approved. Stopping.")
            write_yaml(manifest_path, manifest)
            return
        set_run_state(manifest, "APPROVED", reason="curator_decision")
        parker_out = step_parker(cfg, run_dir, agents_dir, curator_path, provider, manifest)
        upsert_output_manifest(manifest, "post_bundle", parker_out)
        set_run_state(manifest, "POST_BUNDLE_READY", reason="parker_complete")
        write_yaml(manifest_path, manifest)
        print(f"Parker created post bundle: {parker_out}")
        return

    date = args.date or dt.date.today().isoformat()
    run_dir = ensure_run_dir(runs_dir, date, args.slug)

    manifest_path = run_dir / cfg['artifacts'].get('run_manifest', 'run_manifest.yaml')
    manifest = {
        "schema_version": "v1",
        "run": {
            "id": run_dir.name,
            "created_at": now_iso(),
            "mode": "full",
            "date": date,
            "slug": args.slug,
        },
        "inputs": {
            "config": {
                "path": _rel_path(root_dir, cfg_abs),
                "sha256": sha256_file(cfg_abs) if cfg_abs.exists() else None,
            },
            "contracts": {
                "path": _rel_path(root_dir, contracts_abs),
                "sha256": sha256_file(contracts_abs),
            },
            "prompts": prompts_manifest,
            "policy": policy_manifest,
            "provider": cfg.get("providers", {}).get("default", {}),
            "routing": {
                agent: {
                    "provider": (route or {}).get("provider"),
                    "model": (route or {}).get("model"),
                    "prompt_file": (route or {}).get("prompt_file"),
                }
                for agent, route in (cfg.get("agent_routing", {}) or {}).items()
            },
        },
        "outputs": {},
        "events": [{"type": "start", "at": now_iso()}],
    }

    if manifest["inputs"]["config"]["sha256"] is None:
        # Best-effort fallback: compute hash from loaded config dict.
        manifest["inputs"]["config"]["sha256"] = sha256_text(yaml.safe_dump(cfg, sort_keys=False))

    set_run_state(manifest, "DRAFT", reason="start")

    # Write an initial manifest immediately for provenance, even if the run later fails.
    write_yaml(manifest_path, manifest)

    # Ensure curator template is available for user later
    copy_template(templates_dir / "curator_decision.template.md", run_dir / "curator_decision.md")

    provider = StubProvider(stub_output)

    # Run pipeline
    trend = step_trend_scout(cfg, run_dir, agents_dir, contracts, provider, manifest)
    upsert_output_manifest(manifest, "trend_brief", trend)
    write_yaml(manifest_path, manifest)
    ideas = step_theo(cfg, run_dir, agents_dir, contracts, provider, manifest, trend)
    upsert_output_manifest(manifest, "ideas", ideas)
    write_yaml(manifest_path, manifest)
    approved = step_mabel(cfg, run_dir, agents_dir, contracts, provider, manifest, ideas)
    upsert_output_manifest(manifest, "approved_ideas", approved)
    write_yaml(manifest_path, manifest)
    scene_brief = step_rowan_scene_brief(cfg, run_dir, agents_dir, contracts, provider, manifest, approved)
    upsert_output_manifest(manifest, "scene_brief", scene_brief)
    write_yaml(manifest_path, manifest)
    scripts = step_lena(cfg, run_dir, agents_dir, contracts, provider, manifest, scene_brief)
    upsert_output_manifest(manifest, "scripts", scripts)
    write_yaml(manifest_path, manifest)
    scene = step_rowan_scene_plan(cfg, run_dir, agents_dir, contracts, provider, manifest, scene_brief, scripts)
    upsert_output_manifest(manifest, "scene_plan", scene)
    write_yaml(manifest_path, manifest)
    set_run_state(manifest, "RENDERING", reason="evan_start")
    write_yaml(manifest_path, manifest)
    render_report = step_evan(cfg, run_dir, agents_dir, contracts, provider, manifest, scene, scripts)
    upsert_output_manifest(manifest, "render_report", render_report)
    write_yaml(manifest_path, manifest)
    set_run_state(manifest, "QC", reason="qc_start")
    write_yaml(manifest_path, manifest)
    qc_report = step_qc(cfg, run_dir, agents_dir, contracts, provider, manifest, render_report)
    upsert_output_manifest(manifest, "qc_report", qc_report)
    write_yaml(manifest_path, manifest)

    qc_text = read_text(qc_report)
    qc_decision = parse_qc_status(qc_text)
    record_gate(manifest, "qc", qc_decision.status, source=qc_report.name)
    write_yaml(manifest_path, manifest)

    if qc_decision.status == "FAIL" and cfg.get("run_defaults", {}).get("stop_on_qc_fail", True):
        set_run_state(manifest, "STOPPED_QC_FAIL", reason="qc_fail")
        write_text(
            run_dir / "STOPPED_QC_FAIL.md",
            (
                "# STOPPED_QC_FAIL\n\n"
                "QC reported FAIL and stop_on_qc_fail=true.\n"
            ),
        )
        manifest.setdefault("events", []).append({"type": "stopped", "at": now_iso(), "reason": "qc_fail"})
        write_yaml(manifest_path, manifest)
        print("QC failed; stopping before curator review.")
        return

    set_run_state(manifest, "READY_FOR_CURATOR", reason="qc_pass")
    mark_ready_for_curator(run_dir)

    # Validate the manifest itself against contract.
    manifest_text = read_text(manifest_path)
    validate_and_write(
        contracts=contracts,
        artifact_key="run_manifest",
        out_path=manifest_path,
        content=manifest_text,
    )

    print(f"Run complete: {run_dir}")
    print(f"Next: edit {run_dir / 'curator_decision.md'} and re-run with --resume {run_dir}")

if __name__ == "__main__":
    main()
