from __future__ import annotations
import random
from typing import Dict, Any, Optional
from models import Persona, Event

SELF_REF_PHRASES = [
    "I confess", "I fear", "I wonder", "I reckon", "I daresay", "It seems to me",
    "Permit me to say", "I cannot help but think"
]

AUDIENCE_SNIPPETS = [
    "my office mates", "the neighbours", "the lads at the pub", "the parish circle",
    "the local paper", "the recruiting sergeant", "our foreman", "the club"
]

def build_scratchpad(persona: Persona, ev: Optional[Event], reflectiveness: float, creativity: float) -> Dict[str, Any]:
    # Intent type determined by beliefs and reflectiveness
    stance = persona.alignment.get("war", 0.0)
    cautious = reflectiveness > 0.6
    risk = max(0.0, min(1.0, (persona.cognitive_style.get("risk_appetite",0.5) + creativity*0.3) - (0.1 if cautious else -0.05)))
    # Intent heuristic
    if cautious and abs(stance) < 0.2 and random.random() < 0.3:
        intent = "question"
    elif random.random() < risk * 0.2:
        intent = "refrain"
    else:
        intent = "assert"
    confidence = max(0.05, min(0.95, persona.cognitive_style.get("certainty",0.5)*0.8 + (0.1 if intent=="assert" else -0.1)))
    self_ref = random.random() < (0.6 if reflectiveness>0.6 else 0.25)
    audience = random.choice(AUDIENCE_SNIPPETS)
    feeling = "anxious" if stance < -0.4 else ("resolute" if stance > 0.4 else "uncertain")
    # Inner monologue
    if ev:
        topic = f"{ev.title}"
    else:
        topic = "rumours from the wireless"
    thought = f"{'We must be steady' if stance>0.4 else 'Heavens keep us' if stance<-0.4 else 'Best keep our heads'}; thinking on {topic} leaves me {feeling}."
    if self_ref:
        thought = f"{random.choice(SELF_REF_PHRASES)}, {thought.lower()}"
    return {
        "intent": intent,
        "confidence": round(confidence,2),
        "self_reference": self_ref,
        "audience_model": audience,
        "feeling": feeling,
        "risk": round(risk,2),
        "thought": thought
    }
