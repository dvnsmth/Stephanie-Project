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

# ---------------------------
# Utilities
# ---------------------------

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

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
    body = (
        "(Replace this stub with a real provider call.)\n\n"
        "## Inputs Received\n"
        f"- Prompt length: {len(system_prompt)}\n"
        f"- Payload length: {len(user_payload)}\n\n"
        "## Placeholder\n"
        "- This agent was not executed against a real model yet.\n"
    )
    return header + body

# ---------------------------
# Pipeline steps
# ---------------------------

def load_agent_prompt(agents_dir: Path, prompt_file: str) -> str:
    p = agents_dir / prompt_file
    if not p.exists():
        raise FileNotFoundError(f"Missing agent prompt file: {p}")
    return read_text(p)

def step_trend_scout(cfg: dict, run_dir: Path, agents_dir: Path) -> Path:
    prompt = load_agent_prompt(agents_dir, cfg['agent_routing']['trend_scout']['prompt_file'])
    payload = "Window: last 72 hours\nRegion: US\n"
    out = call_llm("trend_scout", prompt, payload)
    out_path = run_dir / cfg['artifacts']['trend_brief']
    write_text(out_path, out)
    return out_path

def step_theo(cfg: dict, run_dir: Path, agents_dir: Path, trend_brief_path: Path) -> Path:
    prompt = load_agent_prompt(agents_dir, cfg['agent_routing']['theo']['prompt_file'])
    payload = (
        f"Batch size: {cfg['run_defaults']['batch_size_ideas']}\n\n"
        "--- trend_brief.md ---\n"
        f"{read_text(trend_brief_path)}\n"
    )
    out = call_llm("theo", prompt, payload)
    out_path = run_dir / cfg['artifacts']['ideas']
    write_text(out_path, out)
    return out_path

def step_mabel(cfg: dict, run_dir: Path, agents_dir: Path, ideas_path: Path) -> Path:
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
    write_text(out_path, out)
    return out_path

def step_lena(cfg: dict, run_dir: Path, agents_dir: Path, approved_ideas_path: Path) -> Path:
    prompt = load_agent_prompt(agents_dir, cfg['agent_routing']['lena']['prompt_file'])
    payload = (
        f"Target length: {cfg['run_defaults']['target_seconds']} seconds\n\n"
        "--- approved_ideas.md ---\n"
        f"{read_text(approved_ideas_path)}\n"
    )
    out = call_llm("lena", prompt, payload)
    out_path = run_dir / cfg['artifacts']['scripts']
    write_text(out_path, out)
    return out_path

def step_rowan(cfg: dict, run_dir: Path, agents_dir: Path, scripts_path: Path) -> Path:
    prompt = load_agent_prompt(agents_dir, cfg['agent_routing']['rowan']['prompt_file'])
    character_bible = Path(cfg['policy']['character_bible'])
    payload = (
        "--- character_bible.md ---\n"
        f"{read_text(character_bible)}\n\n"
        "--- scripts.md ---\n"
        f"{read_text(scripts_path)}\n"
    )
    out = call_llm("rowan", prompt, payload)
    out_path = run_dir / cfg['artifacts']['scene_plan']
    write_text(out_path, out)
    return out_path

def step_evan(cfg: dict, run_dir: Path, agents_dir: Path, scene_plan_path: Path, scripts_path: Path) -> Path:
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
    write_text(report_path, out)
    return report_path

def step_qc(cfg: dict, run_dir: Path, agents_dir: Path, render_report_path: Path) -> Path:
    prompt = load_agent_prompt(agents_dir, cfg['agent_routing']['qc']['prompt_file'])
    payload = (
        "--- render_report.md ---\n"
        f"{read_text(render_report_path)}\n"
    )
    out = call_llm("qc", prompt, payload)
    out_path = run_dir / cfg['artifacts']['qc_report']
    write_text(out_path, out)
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

    # Ensure taste profile exists
    taste_path = root_dir / cfg['policy']['stephanie_taste_profile']
    taste_path.parent.mkdir(parents=True, exist_ok=True)
    if not taste_path.exists():
        write_text(taste_path, "# stephanie_taste_profile.md\n\n(fill in)\n")

    # Resume path flow (after curator decision)
    if args.resume:
        run_dir = Path(args.resume)
        curator_path = run_dir / cfg['artifacts']['curator_decision']
        if not curator_path.exists():
            raise FileNotFoundError(f"Missing curator_decision.md in {run_dir}")
        # Parse simple approval flag
        content = read_text(curator_path).lower()
        approved = "approved: yes" in content
        if not approved:
            print("Curator vetoed or not approved. Stopping.")
            return
        parker_out = step_parker(cfg, run_dir, agents_dir, curator_path)
        print(f"Parker created post bundle: {parker_out}")
        return

    date = args.date or dt.date.today().isoformat()
    run_dir = ensure_run_dir(runs_dir, date, args.slug)

    # Ensure curator template is available for user later
    copy_template(templates_dir / "curator_decision.template.md", run_dir / "curator_decision.md")

    # Run pipeline
    trend = step_trend_scout(cfg, run_dir, agents_dir)
    ideas = step_theo(cfg, run_dir, agents_dir, trend)
    approved = step_mabel(cfg, run_dir, agents_dir, ideas)
    scripts = step_lena(cfg, run_dir, agents_dir, approved)
    scene = step_rowan(cfg, run_dir, agents_dir, scripts)
    render_report = step_evan(cfg, run_dir, agents_dir, scene, scripts)
    qc_report = step_qc(cfg, run_dir, agents_dir, render_report)

    mark_ready_for_curator(run_dir)
    print(f"Run complete: {run_dir}")
    print(f"Next: edit {run_dir / 'curator_decision.md'} and re-run with --resume {run_dir}")

if __name__ == "__main__":
    main()
