from __future__ import annotations

import math
from typing import Iterable, List, Sequence, Tuple

from .domain import Vector2, Vessel, WardNode, World

try:
    from . import _lumen_native  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover - exercised when native module is absent.
    _lumen_native = None


def _kind_bias(kind: str) -> float:
    return {
        "veil": 1.05,
        "stillness": 1.45,
        "silence": 1.25,
        "mercy": 0.85,
        "measure": 0.65,
    }.get(kind, 1.0)


def _python_propagate(
    vessels: Sequence[Tuple[float, ...]],
    nodes: Sequence[Tuple[float, ...]],
    dt: float,
) -> List[Tuple[float, ...]]:
    propagated = []
    for vessel in vessels:
        (
            x,
            y,
            vx,
            vy,
            ax,
            ay,
            susceptibility,
            shielding,
            comms,
            navigation,
            sensors,
            control_link,
            hardpoint_sync,
            exposure,
        ) = vessel
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt
        pressure = 0.0
        for node in nodes:
            nx, ny, reach, intensity, falloff, bias = node
            distance = math.hypot(x - nx, y - ny)
            if distance > reach:
                continue
            attenuation = math.exp(-falloff * (distance / max(reach, 1e-6)))
            effect = intensity * attenuation * susceptibility * max(0.05, 1.0 - shielding) * bias
            pressure += effect
            comms -= effect * 0.025 * dt * bias
            navigation -= effect * 0.018 * dt * (1.0 + bias * 0.2)
            sensors -= effect * 0.021 * dt
            control_link -= effect * 0.014 * dt * bias
            hardpoint_sync -= effect * 0.031 * dt
            exposure += effect * dt
        comms = min(1.0, max(0.0, comms))
        navigation = min(1.0, max(0.0, navigation))
        sensors = min(1.0, max(0.0, sensors))
        control_link = min(1.0, max(0.0, control_link))
        hardpoint_sync = min(1.0, max(0.0, hardpoint_sync))
        propagated.append(
            (
                x,
                y,
                vx,
                vy,
                comms,
                navigation,
                sensors,
                control_link,
                hardpoint_sync,
                exposure,
                pressure,
            )
        )
    return propagated


class PhysicsEngine:
    def __init__(self) -> None:
        self.native_available = _lumen_native is not None

    def advance(self, world: World, dt: float = 1.0) -> None:
        vessels_payload = [self._pack_vessel(vessel) for vessel in world.vessels]
        nodes_payload = [self._pack_node(node) for node in world.ward_nodes]
        if self.native_available:
            results = _lumen_native.propagate(vessels_payload, nodes_payload, float(dt))
        else:
            results = _python_propagate(vessels_payload, nodes_payload, float(dt))
        for vessel, result in zip(world.vessels, results):
            self._unpack_into(vessel, result)

    def _pack_vessel(self, vessel: Vessel) -> Tuple[float, ...]:
        return (
            vessel.position.x,
            vessel.position.y,
            vessel.velocity.x,
            vessel.velocity.y,
            vessel.acceleration.x,
            vessel.acceleration.y,
            vessel.susceptibility,
            vessel.shielding,
            vessel.systems.comms,
            vessel.systems.navigation,
            vessel.systems.sensors,
            vessel.systems.control_link,
            vessel.systems.hardpoint_sync,
            vessel.exposure,
        )

    def _pack_node(self, node: WardNode) -> Tuple[float, ...]:
        return (
            node.position.x,
            node.position.y,
            node.reach,
            node.intensity,
            node.falloff,
            _kind_bias(node.kind),
        )

    def _unpack_into(self, vessel: Vessel, result: Iterable[float]) -> None:
        (
            x,
            y,
            vx,
            vy,
            comms,
            navigation,
            sensors,
            control_link,
            hardpoint_sync,
            exposure,
            pressure,
        ) = result
        vessel.position = Vector2(x, y)
        vessel.velocity = Vector2(vx, vy)
        vessel.systems.comms = comms
        vessel.systems.navigation = navigation
        vessel.systems.sensors = sensors
        vessel.systems.control_link = control_link
        vessel.systems.hardpoint_sync = hardpoint_sync
        vessel.systems.clamp()
        vessel.exposure = exposure
        vessel.notes.append(f"field-pressure:{pressure:.3f}")
