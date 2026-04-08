from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

from .api import serve
from .scenario import ScenarioBook
from .services.simulation import SimulationOrchestrator


def _print(payload: Dict[str, Any], pretty: bool = False) -> None:
    if pretty:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(json.dumps(payload, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lumen-veil",
        description="Interplanetary perimeter doctrine simulator.",
        epilog="Ceremonial forms remain compatible with the older commands: list-scenarios, run, step, inspect-policy, and serve.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    list_cmd = sub.add_parser("rites", aliases=["list-scenarios"], help="List bundled rites of passage.")
    list_cmd.add_argument("--pretty", action="store_true")

    run_cmd = sub.add_parser("conduct", aliases=["run"], help="Conduct a scenario from first witness to verdict.")
    run_cmd.add_argument("--scenario", required=True)
    run_cmd.add_argument("--steps", type=int, default=6)
    run_cmd.add_argument("--dt", type=float, default=1.0)
    run_cmd.add_argument("--pretty", action="store_true")

    step_cmd = sub.add_parser("measure", aliases=["step"], help="Advance the world by measured increments.")
    step_cmd.add_argument("--scenario", required=True)
    step_cmd.add_argument("--steps", type=int, default=1)
    step_cmd.add_argument("--dt", type=float, default=1.0)
    step_cmd.add_argument("--pretty", action="store_true")

    policy_cmd = sub.add_parser("canon", aliases=["inspect-policy"], help="Read the canon for a jurisdiction.")
    policy_cmd.add_argument("--jurisdiction", required=True)
    policy_cmd.add_argument("--pretty", action="store_true")

    serve_cmd = sub.add_parser("gate", aliases=["serve"], help="Open the HTTP gate.")
    serve_cmd.add_argument("--host", default="127.0.0.1")
    serve_cmd.add_argument("--port", type=int, default=8787)

    return parser


def main(argv: Any = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    book = ScenarioBook()

    if args.command in {"rites", "list-scenarios"}:
        _print({"items": book.list()}, pretty=args.pretty)
        return 0

    if args.command in {"canon", "inspect-policy"}:
        profile = book.load_profile(args.jurisdiction)
        orchestrator = SimulationOrchestrator(profile)
        _print(
            {
                "name": profile.name,
                "doctrine": profile.doctrine,
                "rules": list(orchestrator.canon.describe()),
            },
            pretty=args.pretty,
        )
        return 0

    if args.command in {"conduct", "run", "measure", "step"}:
        world = book.load(args.scenario)
        profile = book.load_profile(world.jurisdiction)
        orchestrator = SimulationOrchestrator(profile)
        if args.command in {"conduct", "run"}:
            payload = orchestrator.run(world, steps=args.steps, dt=args.dt)
        else:
            for _ in range(args.steps):
                orchestrator.step(world, dt=args.dt)
            payload = {
                "world": world.summary(),
                "events": [event.to_dict() for event in orchestrator.bus.stream],
                "audit": orchestrator.audit.entries,
                "litany": orchestrator._compose_rite_summary(
                    world,
                    {"steps": args.steps},
                ),
            }
        _print(payload, pretty=args.pretty)
        return 0

    if args.command in {"gate", "serve"}:
        serve(host=args.host, port=args.port)
        return 0

    parser.print_help(sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
