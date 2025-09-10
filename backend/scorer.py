from __future__ import annotations
from typing import Dict, Any, Optional
from models import Persona, Event

# Simple readable scores in [0,1]
def score_temporal(ev: Optional[Event], era: str) -> float:
    return 1.0 if ev else 0.6

def score_voice(tokens_in_lexicon_ratio: float) -> float:
    # Reward staying inside lexicon; allow some out-of-lexicon for creativity
    return max(0.0, min(1.0, 0.6 + 0.4 * tokens_in_lexicon_ratio))

def score_consistency(persona: Persona, text: str) -> float:
    # Very simple stance/text heuristic
    pro_war = any(w in text.lower() for w in ["forward","onwards","to arms","khaki"])
    anti_war = any(w in text.lower() for w in ["pray","mercy","cease","armistice"])
    stance = persona.alignment.get("war", 0.0)
    if pro_war and stance < -0.4: return 0.4
    if anti_war and stance > 0.4: return 0.4
    return 0.8

def composite_score(temporal: float, voice: float, consistency: float, risk: float) -> float:
    base = 0.4*temporal + 0.35*voice + 0.25*consistency
    # Too much risk reduces score a bit
    return max(0.0, min(1.0, base - max(0, risk-0.7)*0.2))
