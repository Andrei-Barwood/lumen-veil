from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List

from .domain import (
    JurisdictionProfile,
    SanctuaryZone,
    Threshold,
    TransitCorridor,
    Vessel,
    WardNode,
    WitnessArray,
    World,
)


class ScenarioBook:
    def __init__(self, root: str = "scenarios", config_root: str = "configs/jurisdictions") -> None:
        self.root = Path(root)
        self.config_root = Path(config_root)

    def load_profile(self, jurisdiction: str) -> JurisdictionProfile:
        path = self.config_root / f"{jurisdiction}.json"
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return JurisdictionProfile.from_dict(payload)

    def list(self) -> List[Dict[str, object]]:
        items = []
        for path in sorted(self.root.glob("*.json")):
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            items.append(
                {
                    "name": payload["name"],
                    "path": str(path),
                    "jurisdiction": payload["jurisdiction"],
                    "description": payload["description"],
                }
            )
        return items

    def load(self, scenario_path: str) -> World:
        path = Path(scenario_path)
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        profile = self.load_profile(payload["jurisdiction"])
        return World(
            scenario=str(payload["name"]),
            jurisdiction=str(payload["jurisdiction"]),
            doctrine=profile.doctrine,
            vessels=[Vessel.from_dict(item) for item in payload.get("vessels", [])],
            witness_arrays=[WitnessArray.from_dict(item) for item in payload.get("witness_arrays", [])],
            ward_nodes=[WardNode.from_dict(item) for item in payload.get("ward_nodes", [])],
            corridors=[TransitCorridor.from_dict(item) for item in payload.get("corridors", [])],
            sanctuaries=[SanctuaryZone.from_dict(item) for item in payload.get("sanctuaries", [])],
            thresholds=[Threshold.from_dict(item) for item in payload.get("thresholds", [])],
            notes=list(payload.get("notes", [])),
        )

    def describe(self, scenario_path: str) -> Dict[str, object]:
        world = self.load(scenario_path)
        return world.summary()
