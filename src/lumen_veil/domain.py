from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Optional


class AegisState(str, Enum):
    OBSERVED = "observed"
    MEASURED = "measured"
    KNOWN = "known"
    BLESSED = "blessed"
    DENIED = "denied"
    SHADOWED = "shadowed"
    DEGRADED = "degraded"
    CONTAINED = "contained"
    RELEASED = "released"
    EXILED = "exiled"


STATE_TRANSITIONS = {
    AegisState.OBSERVED: {
        AegisState.MEASURED,
        AegisState.SHADOWED,
        AegisState.DENIED,
        AegisState.CONTAINED,
        AegisState.RELEASED,
    },
    AegisState.MEASURED: {
        AegisState.KNOWN,
        AegisState.DENIED,
        AegisState.SHADOWED,
        AegisState.CONTAINED,
    },
    AegisState.KNOWN: {
        AegisState.BLESSED,
        AegisState.DENIED,
        AegisState.SHADOWED,
        AegisState.CONTAINED,
        AegisState.RELEASED,
    },
    AegisState.BLESSED: {AegisState.RELEASED, AegisState.SHADOWED},
    AegisState.DENIED: {
        AegisState.SHADOWED,
        AegisState.DEGRADED,
        AegisState.CONTAINED,
        AegisState.EXILED,
    },
    AegisState.SHADOWED: {
        AegisState.DENIED,
        AegisState.DEGRADED,
        AegisState.CONTAINED,
        AegisState.RELEASED,
    },
    AegisState.DEGRADED: {AegisState.CONTAINED, AegisState.RELEASED, AegisState.EXILED},
    AegisState.CONTAINED: {AegisState.DEGRADED, AegisState.RELEASED, AegisState.EXILED},
    AegisState.RELEASED: {AegisState.OBSERVED},
    AegisState.EXILED: set(),
}


@dataclass
class Vector2:
    x: float
    y: float

    def magnitude(self) -> float:
        return math.hypot(self.x, self.y)

    def distance_to(self, other: "Vector2") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def scale(self, factor: float) -> "Vector2":
        return Vector2(self.x * factor, self.y * factor)

    def add(self, other: "Vector2") -> "Vector2":
        return Vector2(self.x + other.x, self.y + other.y)

    def dot(self, other: "Vector2") -> float:
        return self.x * other.x + self.y * other.y

    def normalized(self) -> "Vector2":
        mag = self.magnitude()
        if mag == 0:
            return Vector2(0.0, 0.0)
        return Vector2(self.x / mag, self.y / mag)

    @classmethod
    def from_dict(cls, payload: Dict[str, float]) -> "Vector2":
        return cls(x=float(payload["x"]), y=float(payload["y"]))

    def to_dict(self) -> Dict[str, float]:
        return {"x": self.x, "y": self.y}


@dataclass
class TransitSeal:
    code: str
    covenant: str
    trust: float
    corridor: Optional[str] = None

    @classmethod
    def from_dict(cls, payload: Optional[Dict[str, object]]) -> Optional["TransitSeal"]:
        if not payload:
            return None
        return cls(
            code=str(payload["code"]),
            covenant=str(payload.get("covenant", "unbound")),
            trust=float(payload.get("trust", 0.0)),
            corridor=payload.get("corridor"),
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "code": self.code,
            "covenant": self.covenant,
            "trust": self.trust,
            "corridor": self.corridor,
        }


@dataclass
class TransitPermit:
    corridor: str
    jurisdiction: str
    tier: str
    sacred_clearance: bool = False

    @classmethod
    def from_dict(cls, payload: Optional[Dict[str, object]]) -> Optional["TransitPermit"]:
        if not payload:
            return None
        return cls(
            corridor=str(payload["corridor"]),
            jurisdiction=str(payload["jurisdiction"]),
            tier=str(payload.get("tier", "civil")),
            sacred_clearance=bool(payload.get("sacred_clearance", False)),
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "corridor": self.corridor,
            "jurisdiction": self.jurisdiction,
            "tier": self.tier,
            "sacred_clearance": self.sacred_clearance,
        }


@dataclass
class VesselSystems:
    sensors: float = 1.0
    comms: float = 1.0
    navigation: float = 1.0
    control_link: float = 1.0
    hardpoint_sync: float = 1.0

    def clamp(self) -> None:
        self.sensors = min(1.0, max(0.0, self.sensors))
        self.comms = min(1.0, max(0.0, self.comms))
        self.navigation = min(1.0, max(0.0, self.navigation))
        self.control_link = min(1.0, max(0.0, self.control_link))
        self.hardpoint_sync = min(1.0, max(0.0, self.hardpoint_sync))

    @classmethod
    def from_dict(cls, payload: Optional[Dict[str, object]]) -> "VesselSystems":
        if not payload:
            return cls()
        return cls(
            sensors=float(payload.get("sensors", 1.0)),
            comms=float(payload.get("comms", 1.0)),
            navigation=float(payload.get("navigation", 1.0)),
            control_link=float(payload.get("control_link", 1.0)),
            hardpoint_sync=float(payload.get("hardpoint_sync", 1.0)),
        )

    def to_dict(self) -> Dict[str, float]:
        return {
            "sensors": self.sensors,
            "comms": self.comms,
            "navigation": self.navigation,
            "control_link": self.control_link,
            "hardpoint_sync": self.hardpoint_sync,
        }


@dataclass
class Vessel:
    ident: str
    callsign: str
    allegiance: str
    route: str
    mass: float
    thermal_signature: float
    engine_signature: float
    susceptibility: float
    shielding: float
    position: Vector2
    velocity: Vector2
    acceleration: Vector2
    seal: Optional[TransitSeal] = None
    permit: Optional[TransitPermit] = None
    state: AegisState = AegisState.OBSERVED
    systems: VesselSystems = field(default_factory=VesselSystems)
    exposure: float = 0.0
    classification: str = "unknown"
    behavior: str = "silent"
    notes: List[str] = field(default_factory=list)
    history: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "Vessel":
        return cls(
            ident=str(payload["ident"]),
            callsign=str(payload["callsign"]),
            allegiance=str(payload.get("allegiance", "unknown")),
            route=str(payload.get("route", "unbound")),
            mass=float(payload.get("mass", 1.0)),
            thermal_signature=float(payload.get("thermal_signature", 0.5)),
            engine_signature=float(payload.get("engine_signature", 0.5)),
            susceptibility=float(payload.get("susceptibility", 0.5)),
            shielding=float(payload.get("shielding", 0.2)),
            position=Vector2.from_dict(payload["position"]),
            velocity=Vector2.from_dict(payload["velocity"]),
            acceleration=Vector2.from_dict(payload.get("acceleration", {"x": 0.0, "y": 0.0})),
            seal=TransitSeal.from_dict(payload.get("seal")),
            permit=TransitPermit.from_dict(payload.get("permit")),
            state=AegisState(payload.get("state", AegisState.OBSERVED.value)),
            systems=VesselSystems.from_dict(payload.get("systems")),
        )

    def transition(self, target: AegisState, reason: str) -> None:
        if target == self.state:
            if reason:
                self.history.append(f"{self.state.value}:{reason}")
            return
        allowed = STATE_TRANSITIONS[self.state]
        if target not in allowed:
            raise ValueError(f"invalid state transition {self.state.value} -> {target.value}")
        self.state = target
        if reason:
            self.history.append(f"{self.state.value}:{reason}")

    def subsystem_health(self) -> float:
        return (
            self.systems.sensors
            + self.systems.comms
            + self.systems.navigation
            + self.systems.control_link
            + self.systems.hardpoint_sync
        ) / 5.0

    def to_dict(self) -> Dict[str, object]:
        return {
            "ident": self.ident,
            "callsign": self.callsign,
            "allegiance": self.allegiance,
            "route": self.route,
            "mass": self.mass,
            "thermal_signature": self.thermal_signature,
            "engine_signature": self.engine_signature,
            "susceptibility": self.susceptibility,
            "shielding": self.shielding,
            "position": self.position.to_dict(),
            "velocity": self.velocity.to_dict(),
            "acceleration": self.acceleration.to_dict(),
            "seal": self.seal.to_dict() if self.seal else None,
            "permit": self.permit.to_dict() if self.permit else None,
            "state": self.state.value,
            "systems": self.systems.to_dict(),
            "exposure": self.exposure,
            "classification": self.classification,
            "behavior": self.behavior,
            "notes": list(self.notes),
            "history": list(self.history),
        }


@dataclass
class WitnessArray:
    name: str
    position: Vector2
    reach: float
    fidelity: float
    noise_floor: float

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "WitnessArray":
        return cls(
            name=str(payload["name"]),
            position=Vector2.from_dict(payload["position"]),
            reach=float(payload.get("reach", 100.0)),
            fidelity=float(payload.get("fidelity", 0.9)),
            noise_floor=float(payload.get("noise_floor", 0.05)),
        )


@dataclass
class WardNode:
    name: str
    kind: str
    position: Vector2
    reach: float
    intensity: float
    falloff: float
    jurisdiction: str

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "WardNode":
        return cls(
            name=str(payload["name"]),
            kind=str(payload.get("kind", "veil")),
            position=Vector2.from_dict(payload["position"]),
            reach=float(payload.get("reach", 80.0)),
            intensity=float(payload.get("intensity", 0.4)),
            falloff=float(payload.get("falloff", 1.0)),
            jurisdiction=str(payload.get("jurisdiction", "neutral")),
        )


@dataclass
class TransitCorridor:
    name: str
    jurisdiction: str
    start: Vector2
    end: Vector2
    width: float
    sacred: bool = False

    def distance_to(self, point: Vector2) -> float:
        px = point.x
        py = point.y
        x1 = self.start.x
        y1 = self.start.y
        x2 = self.end.x
        y2 = self.end.y
        dx = x2 - x1
        dy = y2 - y1
        denom = dx * dx + dy * dy
        if denom == 0:
            return point.distance_to(self.start)
        t = ((px - x1) * dx + (py - y1) * dy) / denom
        t = max(0.0, min(1.0, t))
        proj = Vector2(x1 + t * dx, y1 + t * dy)
        return point.distance_to(proj)

    def contains(self, point: Vector2) -> bool:
        return self.distance_to(point) <= self.width

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "TransitCorridor":
        return cls(
            name=str(payload["name"]),
            jurisdiction=str(payload["jurisdiction"]),
            start=Vector2.from_dict(payload["start"]),
            end=Vector2.from_dict(payload["end"]),
            width=float(payload.get("width", 15.0)),
            sacred=bool(payload.get("sacred", False)),
        )


@dataclass
class SanctuaryZone:
    name: str
    jurisdiction: str
    center: Vector2
    radius: float

    def contains(self, point: Vector2) -> bool:
        return self.center.distance_to(point) <= self.radius

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "SanctuaryZone":
        return cls(
            name=str(payload["name"]),
            jurisdiction=str(payload["jurisdiction"]),
            center=Vector2.from_dict(payload["center"]),
            radius=float(payload.get("radius", 20.0)),
        )


@dataclass
class Threshold:
    name: str
    jurisdiction: str
    anchor: Vector2
    radius: float

    def contains(self, point: Vector2) -> bool:
        return self.anchor.distance_to(point) <= self.radius

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "Threshold":
        return cls(
            name=str(payload["name"]),
            jurisdiction=str(payload["jurisdiction"]),
            anchor=Vector2.from_dict(payload["anchor"]),
            radius=float(payload.get("radius", 12.0)),
        )


@dataclass
class WitnessRecord:
    vessel_id: str
    confidence: float
    thermal: float
    engine: float
    transponder: float
    behavior: float
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "vessel_id": self.vessel_id,
            "confidence": self.confidence,
            "thermal": self.thermal,
            "engine": self.engine,
            "transponder": self.transponder,
            "behavior": self.behavior,
            "notes": list(self.notes),
        }


@dataclass
class IdentityAssessment:
    vessel_id: str
    classification: str
    behavior: str
    anomaly_score: float
    corridor_violation: bool
    sacred_violation: bool
    permit_present: bool
    seal_present: bool
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "vessel_id": self.vessel_id,
            "classification": self.classification,
            "behavior": self.behavior,
            "anomaly_score": self.anomaly_score,
            "corridor_violation": self.corridor_violation,
            "sacred_violation": self.sacred_violation,
            "permit_present": self.permit_present,
            "seal_present": self.seal_present,
            "reasons": list(self.reasons),
        }


@dataclass
class CanonRule:
    name: str
    priority: int
    match: Dict[str, object]
    action: str
    target_state: AegisState
    reason_code: str
    effects: Dict[str, float] = field(default_factory=dict)
    emit: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "CanonRule":
        return cls(
            name=str(payload["name"]),
            priority=int(payload.get("priority", 100)),
            match=dict(payload.get("match", {})),
            action=str(payload["action"]),
            target_state=AegisState(payload["target_state"]),
            reason_code=str(payload["reason_code"]),
            effects=dict(payload.get("effects", {})),
            emit=list(payload.get("emit", [])),
        )


@dataclass
class JurisdictionProfile:
    name: str
    doctrine: str
    ambiguity_tolerance: float
    release_bias: float
    rules: List[CanonRule]

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "JurisdictionProfile":
        return cls(
            name=str(payload["name"]),
            doctrine=str(payload["doctrine"]),
            ambiguity_tolerance=float(payload.get("ambiguity_tolerance", 0.5)),
            release_bias=float(payload.get("release_bias", 0.2)),
            rules=[CanonRule.from_dict(item) for item in payload.get("rules", [])],
        )


@dataclass
class CanonDecision:
    action: str
    target_state: AegisState
    reason_code: str
    rule_name: str
    effects: Dict[str, float]
    emitted_events: List[str]
    explanation: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "action": self.action,
            "target_state": self.target_state.value,
            "reason_code": self.reason_code,
            "rule_name": self.rule_name,
            "effects": dict(self.effects),
            "emitted_events": list(self.emitted_events),
            "explanation": self.explanation,
        }


@dataclass
class World:
    scenario: str
    jurisdiction: str
    doctrine: str
    vessels: List[Vessel]
    witness_arrays: List[WitnessArray]
    ward_nodes: List[WardNode]
    corridors: List[TransitCorridor]
    sanctuaries: List[SanctuaryZone]
    thresholds: List[Threshold]
    notes: List[str] = field(default_factory=list)
    tick: int = 0
    time: float = 0.0

    def iter_vessels(self) -> Iterable[Vessel]:
        return tuple(self.vessels)

    def vessel_map(self) -> Dict[str, Vessel]:
        return {vessel.ident: vessel for vessel in self.vessels}

    def summary(self) -> Dict[str, object]:
        return {
            "scenario": self.scenario,
            "jurisdiction": self.jurisdiction,
            "doctrine": self.doctrine,
            "tick": self.tick,
            "time": self.time,
            "vessels": [v.to_dict() for v in self.vessels],
            "notes": list(self.notes),
        }
