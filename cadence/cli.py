"""The `cadence` CLI: `cadence run ...` and `cadence doctor` (docs/TASKS.md)."""

from __future__ import annotations

import argparse
import sys

from .config import Config


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    parser = argparse.ArgumentParser(
        prog="cadence", description="Vision-driven Android UI automation."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="run a routine from plain-English goals or profile tasks")
    p_run.add_argument("goals", nargs="*",
                       help="freeform goal(s), or task id(s) when --profile is set")
    p_run.add_argument("--config", default=None)
    p_run.add_argument("--profile", default=None)
    p_run.add_argument("--dry-run", action="store_true",
                       help="plan and log decisions but inject nothing")
    p_run.add_argument("--no-humanization", action="store_true")
    p_run.add_argument("--max-steps", type=int, default=None)
    p_run.add_argument("--yes", action="store_true",
                       help="auto-approve the plan (sensitive actions still pause)")
    p_run.add_argument("--seed", type=int, default=None)

    p_doc = sub.add_parser("doctor", help="validate device + provider + config")
    p_doc.add_argument("--config", default=None)

    args = parser.parse_args(argv)

    if args.cmd == "doctor":
        from .doctor import run_doctor
        return run_doctor(_load(args.config))

    if args.cmd == "run":
        cfg = _load(args.config)
        if args.max_steps:
            cfg.run.max_steps = args.max_steps
        if args.dry_run:
            cfg.run.dry_run = True
        if args.no_humanization:
            cfg.humanization.enabled = False
        return _do_run(cfg, args)

    return 0


def _load(path) -> Config:
    try:
        return Config.load(path)
    except FileNotFoundError:
        print(f"config not found: {path}", file=sys.stderr)
        raise SystemExit(2)
    except Exception as exc:
        print(f"config error: {exc}", file=sys.stderr)
        raise SystemExit(2)


def _resolve_goals(goals, profile_path):
    if not profile_path:
        return list(goals)
    import yaml
    with open(profile_path, encoding="utf-8") as fh:
        profile = yaml.safe_load(fh) or {}
    tasks = profile.get("tasks", {})
    resolved = []
    for g in goals:
        task = tasks.get(g)
        resolved.append(task.get("goal", g) if isinstance(task, dict) else g)
    return resolved


def _do_run(cfg, args) -> int:
    from .backends import build_backend
    from .loop import Engine
    from .planner import confirm, plan
    from .providers import build_provider
    from .runlog import RunLog

    profile_path = None
    if args.profile:
        profile_path = (args.profile if args.profile.endswith((".yaml", ".yml"))
                        else f"profiles/{args.profile}.yaml")

    raw_goals = _resolve_goals(args.goals, profile_path)
    if not raw_goals:
        print("nothing to run — pass a goal, or --profile <id> <task>", file=sys.stderr)
        return 2

    steps = []
    for goal in raw_goals:
        steps.extend(plan(goal))

    if cfg.run.confirm_before_execute and not confirm(steps, assume_yes=args.yes):
        print("aborted.")
        return 1

    backend = build_backend(cfg.device)
    provider = build_provider(cfg.provider)
    runlog = RunLog(cfg.run.log_dir)
    engine = Engine(cfg, provider, backend, runlog,
                    seed=args.seed, humanize_cfg=_humanize_cfg(cfg.humanization))
    try:
        results = engine.run(steps, dry_run=cfg.run.dry_run, assume_yes=args.yes)
    finally:
        runlog.close()

    print(f"\nrun complete — log: {runlog.dir}")
    for step, status in results:
        print(f"  [{status}] {step.goal}")
    return 0


def _humanize_cfg(h):
    from .humanize import HumanizeConfig
    return HumanizeConfig(
        enabled=h.enabled,
        timing=h.timing,
        base_delay_ms=h.base_delay_ms,
        tap_jitter=h.tap_jitter,
        tap_duration_ms=tuple(h.tap_duration_ms),
        swipe_curve=h.swipe_curve,
        imperfection_rate=h.imperfection_rate,
    )
