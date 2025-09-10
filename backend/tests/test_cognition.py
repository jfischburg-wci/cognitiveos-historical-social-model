from cognition import build_scratchpad
from models import Persona, Event

def test_scratchpad_shape():
    p = Persona(id="p", handle="h", era="1914-08", region="Europe-West",
                occupation="clerk", alignment={"war":0.1}, voice={}, followers=[], following=[],
                cognitive_style={"reflectiveness":0.6,"certainty":0.5,"risk_appetite":0.4,"irony":0.1})
    ev = Event(id="e", date="1914-08-04", title="UK declares war", summary="UK declares war on Germany.", region="Europe-West", citations=[])
    sp = build_scratchpad(p, ev, 0.6, 0.4)
    assert "intent" in sp and "confidence" in sp and "thought" in sp
