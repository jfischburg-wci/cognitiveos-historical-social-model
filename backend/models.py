from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class Event(BaseModel):
    id: str
    date: str  # YYYY-MM-DD
    title: str
    summary: str
    region: str
    citations: List[str] = []

class Persona(BaseModel):
    id: str
    handle: str
    era: str
    region: str
    occupation: str
    alignment: Dict[str, float]  # topic -> stance [-1,1]
    voice: Dict[str, Any]
    followers: List[str] = []
    following: List[str] = []
    cognitive_style: Dict[str, float] = {}  # reflectiveness, certainty, irony, risk_appetite

class Post(BaseModel):
    id: str
    persona_id: str
    handle: str
    timestamp: str
    text: str
    features: Dict[str, Any]
    grounding: List[Dict[str, Any]] = []
    meta: Optional[Dict[str, Any]] = None  # scratchpad (optional, debug only)
