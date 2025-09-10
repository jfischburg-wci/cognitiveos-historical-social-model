from __future__ import annotations
import math, random, time
from typing import Dict, List, Tuple
from models import Persona, Event

class ActivityModel:
    def __init__(self, personas: List[Persona], events: List[Event], now_ts: float):
        self.personas = personas
        self.events = events
        self.base = 0.03
        self.self_boost = 0.06
        self.follow_boost = 0.04
        self.tau = 12.0
        self.last_posts: Dict[str, List[float]] = {p.id: [] for p in personas}
        self.event_times = self._prepare_event_times(now_ts)
        self.region_bias = {"Europe-West": 1.0, "Europe-Central": 1.0, "Europe-Balkans": 1.2, "Europe-North": 0.9, "Europe-South": 0.9}

        self.followers: Dict[str, List[str]] = {p.id: [] for p in personas}
        id2p = {p.id: p for p in personas}
        for p in personas:
            for f in p.following:
                self.followers[f].append(p.id)

    def _prepare_event_times(self, now_ts: float) -> List[Tuple[float, Event]]:
        sorted_events = sorted(self.events, key=lambda e: e.date)
        tlist = []
        for i, ev in enumerate(sorted_events):
            t = now_ts + i * 10.0  # demo: every 10s a new event "arrives"
            tlist.append((t, ev))
        return tlist

    def intensity(self, persona: Persona, t: float) -> float:
        lam = self.base
        for ts in self.last_posts[persona.id][-5:]:
            lam += self.self_boost * math.exp(-(t - ts) / self.tau)
        # rough social excitation
        recent = 0
        for ts_list in self.last_posts.values():
            if ts_list and (t - ts_list[-1]) < 6.0:
                recent += 1
        lam += min(0.1, recent * 0.001)
        # event spike
        for et, ev in self.event_times:
            dt = t - et
            if 0 <= dt < 15.0:
                spike = 0.15 * math.exp(-dt / 6.0)
                if persona.region == ev.region: spike *= 1.6
                lam += spike
        # region baseline
        lam *= {"Europe-Balkans":1.1}.get(persona.region, 1.0)
        return lam

    def register_post(self, persona_id: str, ts: float):
        self.last_posts[persona_id].append(ts)
        if len(self.last_posts[persona_id]) > 50:
            self.last_posts[persona_id] = self.last_posts[persona_id][-50:]
