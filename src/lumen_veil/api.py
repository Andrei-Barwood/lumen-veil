from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, Optional

from .scenario import ScenarioBook
from .services.simulation import SimulationOrchestrator


class SimulationAPI:
    def __init__(self, book: Optional[ScenarioBook] = None) -> None:
        self.book = book or ScenarioBook()

    def health(self) -> Dict[str, object]:
        return {"status": "ok", "service": "lumen-veil-api"}

    def list_scenarios(self) -> Dict[str, object]:
        return {"items": self.book.list()}

    def run(self, scenario: str, steps: int = 6, dt: float = 1.0) -> Dict[str, object]:
        world = self.book.load(scenario)
        profile = self.book.load_profile(world.jurisdiction)
        orchestrator = SimulationOrchestrator(profile)
        return orchestrator.run(world, steps=steps, dt=dt)

    def policy(self, jurisdiction: str) -> Dict[str, object]:
        profile = self.book.load_profile(jurisdiction)
        return {
            "name": profile.name,
            "doctrine": profile.doctrine,
            "ambiguity_tolerance": profile.ambiguity_tolerance,
            "release_bias": profile.release_bias,
            "rules": list(SimulationOrchestrator(profile).canon.describe()),
        }


def make_handler(api: SimulationAPI):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/health":
                self._send(api.health())
                return
            if self.path == "/scenarios":
                self._send(api.list_scenarios())
                return
            if self.path.startswith("/policy/"):
                jurisdiction = self.path.rsplit("/", 1)[-1]
                self._send(api.policy(jurisdiction))
                return
            self._send({"error": "not found"}, status=HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/run":
                self._send({"error": "not found"}, status=HTTPStatus.NOT_FOUND)
                return
            size = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(size) or b"{}")
            scenario = payload["scenario"]
            steps = int(payload.get("steps", 6))
            dt = float(payload.get("dt", 1.0))
            self._send(api.run(scenario=scenario, steps=steps, dt=dt))

        def log_message(self, *_args) -> None:
            return

        def _send(self, payload: Dict[str, object], status: HTTPStatus = HTTPStatus.OK) -> None:
            body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
            self.send_response(status.value)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return Handler


def serve(host: str = "127.0.0.1", port: int = 8787) -> None:
    api = SimulationAPI()
    server = ThreadingHTTPServer((host, port), make_handler(api))
    try:
        server.serve_forever()
    finally:
        server.server_close()
