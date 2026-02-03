#!/usr/bin/env python3
"""run_pipeline.py — The Stephanie Project (Phase 1 Controller)

Phase 1 is intentionally provider-agnostic and runs in STUB mode by default.
Replace `call_llm()` with your chosen provider client (Claude SDK / OpenAI Responses / etc.).
"""

import argparse
import datetime as dt
import os
from pathlib import Path
import yaml
import shutil

try:
    # When executed as a module: python -m scripts.run_pipeline
    from scripts.artifact_contracts import load_contracts, validate_artifact
    from scripts.provenance import sha256_file, sha256_text
except ImportError:
    # When executed as a script: python scripts/run_pipeline.py
    from artifact_contracts import load_contracts, validate_artifact
    from provenance import sha256_file, sha256_text

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
            "## Rejected (rest)\n"
            "- **Title:** (stub rejected idea)\n"
            "- **Reason (1 line):** Too performative for the tone rules.\n"
        )

    if agent_name == "lena":
        return (
            "## The Lunchbox That Won’t Close\n\n"
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

def call_llm(agent_name: str, system_prompt: str, user_payload: str) -> str:
    """Stub implementation.

    Replace with:
      - Claude Agent SDK client call, or
      - OpenAI Responses API call, etc.

    The contract: return the agent's markdown output.
    """
    header = f"# STUB OUTPUT — {agent_name}\nGenerated at: {now_iso()}\n\n"
    meta = (
        "(Replace this stub with a real provider call.)\n\n"
        "## Inputs Received\n"
        f"- Prompt length: {len(system_prompt)}\n"
        f"- Payload length: {len(user_payload)}\n\n"
        "---\n\n"
    )
    return header + meta + stub_output(agent_name, user_payload)


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

# ---------------------------
# Pipeline steps
# ---------------------------

def load_agent_prompt(agents_dir: Path, prompt_file: str) -> str:
    p = agents_dir / prompt_file
    if not p.exists():
        raise FileNotFoundError(f"Missing agent prompt file: {p}")
    return read_text(p)

def step_trend_scout(cfg: dict, run_dir: Path, agents_dir: Path, contracts: dict) -> Path:
    prompt = load_agent_prompt(agents_dir, cfg['agent_routing']['trend_scout']['prompt_file'])
    payload = "Window: last 72 hours\nRegion: US\n"
    out = call_llm("trend_scout", prompt, payload)
    out_path = run_dir / cfg['artifacts']['trend_brief']
    validate_and_write(contracts=contracts, artifact_key="trend_brief", out_path=out_path, content=out)
    return out_path

def step_theo(cfg: dict, run_dir: Path, agents_dir: Path, contracts: dict, trend_brief_path: Path) -> Path:
    prompt = load_agent_prompt(agents_dir, cfg['agent_routing']['theo']['prompt_file'])
    payload = (
        f"Batch size: {cfg['run_defaults']['batch_size_ideas']}\n\n"
        "--- trend_brief.md ---\n"
        f"{read_text(trend_brief_path)}\n"
    )
    out = call_llm("theo", prompt, payload)
    out_path = run_dir / cfg['artifacts']['ideas']
    validate_and_write(contracts=contracts, artifact_key="ideas", out_path=out_path, content=out)
    return out_path

def step_mabel(cfg: dict, run_dir: Path, agents_dir: Path, contracts: dict, ideas_path: Path) -> Path:
    prompt = load_agent_prompt(agents_dir, cfg['agent_routing']['mabel']['prompt_file'])
    taste_path = Path(cfg['policy']['stephanie_taste_profile'])
    payload = (
        "--- stephanie_taste_profile.md ---\n"
        f"{read_text(taste_path)}\n\n"
        "--- ideas.md ---\n"
        f"{read_text(ideas_path)}\n"
    )
    out = call_llm("mabel", prompt, payload)
    out_path = run_dir / cfg['artifacts']['approved_ideas']
    validate_and_write(contracts=contracts, artifact_key="approved_ideas", out_path=out_path, content=out)
    return out_path

def step_rowan_scene_brief(cfg: dict, run_dir: Path, agents_dir: Path, contracts: dict, approved_ideas_path: Path) -> Path:
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
    out = call_llm("rowan", prompt, payload)
    out_path = run_dir / cfg['artifacts']['scene_brief']
    validate_and_write(contracts=contracts, artifact_key="scene_brief", out_path=out_path, content=out)
    return out_path


def step_lena(cfg: dict, run_dir: Path, agents_dir: Path, contracts: dict, scene_brief_path: Path) -> Path:
    prompt = load_agent_prompt(agents_dir, cfg['agent_routing']['lena']['prompt_file'])
    character_bible = Path(cfg['policy']['character_bible'])
    payload = (
        f"Target length: {cfg['run_defaults']['target_seconds']} seconds\n\n"
        "--- character_bible.md ---\n"
        f"{read_text(character_bible)}\n\n"
        "--- scene_brief.md ---\n"
        f"{read_text(scene_brief_path)}\n"
    )
    out = call_llm("lena", prompt, payload)
    out_path = run_dir / cfg['artifacts']['scripts']
    validate_and_write(contracts=contracts, artifact_key="scripts", out_path=out_path, content=out)
    return out_path

def step_rowan_scene_plan(
    cfg: dict,
    run_dir: Path,
    agents_dir: Path,
    contracts: dict,
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
    out = call_llm("rowan", prompt, payload)
    out_path = run_dir / cfg['artifacts']['scene_plan']
    validate_and_write(contracts=contracts, artifact_key="scene_plan", out_path=out_path, content=out)
    return out_path

def step_evan(cfg: dict, run_dir: Path, agents_dir: Path, contracts: dict, scene_plan_path: Path, scripts_path: Path) -> Path:
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
    out = call_llm("evan", prompt, payload)

    # Create prompt bundle folder
    bundle = run_dir / "render_prompts" / "v1"
    bundle.mkdir(parents=True, exist_ok=True)
    write_text(bundle / "shot_01.txt", "(stub) shot prompt goes here\n")
    write_text(bundle / "voice.txt", "(stub) voice prompt goes here\n")
    write_text(bundle / "edit_notes.md", "(stub) edit/assembly notes\n")
    report_path = run_dir / "render_report.md"
    validate_and_write(contracts=contracts, artifact_key="render_report", out_path=report_path, content=out)
    return report_path

def step_qc(cfg: dict, run_dir: Path, agents_dir: Path, contracts: dict, render_report_path: Path) -> Path:
    prompt = load_agent_prompt(agents_dir, cfg['agent_routing']['qc']['prompt_file'])
    payload = (
        "--- render_report.md ---\n"
        f"{read_text(render_report_path)}\n"
    )
    out = call_llm("qc", prompt, payload)
    out_path = run_dir / cfg['artifacts']['qc_report']
    validate_and_write(contracts=contracts, artifact_key="qc_report", out_path=out_path, content=out)
    return out_path

def mark_ready_for_curator(run_dir: Path) -> None:
    write_text(run_dir / "READY_FOR_CURATOR.md",
               "# READY_FOR_CURATOR\n\nAll artifacts generated. Add curator_decision.md to proceed.\n")

def step_parker(cfg: dict, run_dir: Path, agents_dir: Path, curator_decision_path: Path) -> Path:
    prompt = load_agent_prompt(agents_dir, cfg['agent_routing']['parker']['prompt_file'])
    payload = read_text(curator_decision_path)
    out = call_llm("parker", prompt, payload)

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
                "path": str(prompt_path.relative_to(root_dir)).replace("\\", "/"),
                "sha256": sha256_file(prompt_path),
            }
        else:
            prompts_manifest[agent_name] = {
                "path": str(prompt_path).replace("\\", "/"),
                "sha256": None,
            }

    # Ensure taste profile exists
    taste_path = root_dir / cfg['policy']['stephanie_taste_profile']
    taste_path.parent.mkdir(parents=True, exist_ok=True)
    if not taste_path.exists():
        write_text(taste_path, "# stephanie_taste_profile.md\n\n(fill in)\n")

    # Resume path flow (after curator decision)
    if args.resume:
        run_dir = Path(args.resume)
        manifest_path = run_dir / cfg['artifacts'].get('run_manifest', 'run_manifest.yaml')
        manifest = {
            "schema_version": "v1",
            "run": {
                "id": run_dir.name,
                "created_at": now_iso(),
                "mode": "resume",
            },
            "inputs": {
                "config": {
                    "path": str(cfg_abs.relative_to(root_dir)).replace("\\", "/") if cfg_abs.exists() else str(cfg_abs),
                    "sha256": sha256_file(cfg_abs) if cfg_abs.exists() else None,
                },
                "contracts": {
                    "path": str(contracts_abs.relative_to(root_dir)).replace("\\", "/"),
                    "sha256": sha256_file(contracts_abs),
                },
                "prompts": prompts_manifest,
                "provider": cfg.get("providers", {}).get("default", {}),
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
                    manifest = existing
            except Exception:
                pass

        curator_path = run_dir / cfg['artifacts']['curator_decision']
        if not curator_path.exists():
            raise FileNotFoundError(f"Missing curator_decision.md in {run_dir}")
        # Parse simple approval flag
        content = read_text(curator_path).lower()
        approved = "approved: yes" in content
        if not approved:
            print("Curator vetoed or not approved. Stopping.")
            write_yaml(manifest_path, manifest)
            return
        parker_out = step_parker(cfg, run_dir, agents_dir, curator_path)
        upsert_output_manifest(manifest, "post_bundle", parker_out)
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
                "path": str(cfg_abs.relative_to(root_dir)).replace("\\", "/") if cfg_abs.exists() else str(cfg_abs),
                "sha256": sha256_file(cfg_abs) if cfg_abs.exists() else None,
            },
            "contracts": {
                "path": str(contracts_abs.relative_to(root_dir)).replace("\\", "/"),
                "sha256": sha256_file(contracts_abs),
            },
            "prompts": prompts_manifest,
            "provider": cfg.get("providers", {}).get("default", {}),
        },
        "outputs": {},
        "events": [{"type": "start", "at": now_iso()}],
    }

    if manifest["inputs"]["config"]["sha256"] is None:
        # Best-effort fallback: compute hash from loaded config dict.
        manifest["inputs"]["config"]["sha256"] = sha256_text(yaml.safe_dump(cfg, sort_keys=False))

    # Write an initial manifest immediately for provenance, even if the run later fails.
    write_yaml(manifest_path, manifest)

    # Ensure curator template is available for user later
    copy_template(templates_dir / "curator_decision.template.md", run_dir / "curator_decision.md")

    # Run pipeline
    trend = step_trend_scout(cfg, run_dir, agents_dir, contracts)
    upsert_output_manifest(manifest, "trend_brief", trend)
    write_yaml(manifest_path, manifest)
    ideas = step_theo(cfg, run_dir, agents_dir, contracts, trend)
    upsert_output_manifest(manifest, "ideas", ideas)
    write_yaml(manifest_path, manifest)
    approved = step_mabel(cfg, run_dir, agents_dir, contracts, ideas)
    upsert_output_manifest(manifest, "approved_ideas", approved)
    write_yaml(manifest_path, manifest)
    scene_brief = step_rowan_scene_brief(cfg, run_dir, agents_dir, contracts, approved)
    upsert_output_manifest(manifest, "scene_brief", scene_brief)
    write_yaml(manifest_path, manifest)
    scripts = step_lena(cfg, run_dir, agents_dir, contracts, scene_brief)
    upsert_output_manifest(manifest, "scripts", scripts)
    write_yaml(manifest_path, manifest)
    scene = step_rowan_scene_plan(cfg, run_dir, agents_dir, contracts, scene_brief, scripts)
    upsert_output_manifest(manifest, "scene_plan", scene)
    write_yaml(manifest_path, manifest)
    render_report = step_evan(cfg, run_dir, agents_dir, contracts, scene, scripts)
    upsert_output_manifest(manifest, "render_report", render_report)
    write_yaml(manifest_path, manifest)
    qc_report = step_qc(cfg, run_dir, agents_dir, contracts, render_report)
    upsert_output_manifest(manifest, "qc_report", qc_report)
    write_yaml(manifest_path, manifest)

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
