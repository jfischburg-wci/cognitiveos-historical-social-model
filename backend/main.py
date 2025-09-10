from __future__ import annotations
import asyncio, json, os, random, time
from datetime import datetime, timezone
from typing import List, Dict, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from models import Persona, Event, Post
from personas import sample_personas
from diffusion import ActivityModel
from generator import two_pass_generate, load_lexicon
from settings import RuntimeSettings

APP_ERA = "1914-08"
settings = RuntimeSettings()

app = FastAPI(title="TimeStream 2‑Pass", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data load ---
BASE = os.path.dirname(__file__)
with open(os.path.join(BASE, "data", "events_1914.json"), "r", encoding="utf-8") as f:
    EVENTS: List[Event] = [Event(**e) for e in json.load(f)]

LEXICON = load_lexicon(os.path.join(BASE, "data", "lexicon_1910s_en.txt"))
PERSONAS: List[Persona] = sample_personas(60, APP_ERA)
ID2P: Dict[str, Persona] = {p.id: p for p in PERSONAS}

activity = ActivityModel(PERSONAS, EVENTS, time.time())

@app.get("/health")
def health():
    return {"status": "ok", "personas": len(PERSONAS), "events": len(EVENTS), "era": APP_ERA}

@app.get("/events")
def get_events():
    return [e.model_dump() for e in EVENTS]

@app.get("/personas")
def get_personas():
    return [{
        "id": p.id, "handle": p.handle, "era": p.era, "region": p.region,
        "occupation": p.occupation, "alignment": p.alignment, "voice": p.voice,
        "followers": len(p.followers), "following": len(p.following),
        "cognitive_style": p.cognitive_style
    } for p in PERSONAS]

@app.get("/settings")
def get_settings():
    return {"reflectiveness": settings.reflectiveness, "creativity": settings.creativity, "debug_meta": settings.debug_meta}

@app.post("/settings")
def set_settings(data: Dict[str, float]):
    settings.reflectiveness = float(data.get("reflectiveness", settings.reflectiveness))
    settings.creativity = float(data.get("creativity", settings.creativity))
    settings.debug_meta = bool(data.get("debug_meta", settings.debug_meta))
    return get_settings()

# --- WebSocket stream ---
clients: List[WebSocket] = []

async def stream_loop(ws: WebSocket, reflect: float, create: float, debug_meta: bool):
    await ws.accept()
    clients.append(ws)
    try:
        while True:
            t = time.time()
            # pick active personas
            active = []
            for p in PERSONAS:
                lam = activity.intensity(p, t)
                if random.random() < min(0.5, lam):
                    active.append(p)
            # map events to current demo time window
            current_event: Optional[Event] = None
            for et, ev in activity.event_times:
                if 0 <= (t - et) < 6.0:
                    current_event = ev
                    break
            posts: List[Post] = []
            for p in active[:4]:  # cap per tick
                now_iso = datetime.now(timezone.utc).isoformat()
                post = two_pass_generate(p, APP_ERA, now_iso, current_event, LEXICON, reflect, create, include_meta=debug_meta)
                if post:
                    posts.append(post)
                    activity.register_post(p.id, t)
            if posts:
                payload = {"type": "posts", "data": [po.model_dump() for po in posts]}
                # broadcast to all connected
                stale = []
                for c in clients:
                    if c.client_state == WebSocketState.CONNECTED:
                        await c.send_json(payload)
                    else:
                        stale.append(c)
                for s in stale:
                    if s in clients:
                        clients.remove(s)
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        if ws in clients:
            clients.remove(ws)

@app.websocket("/ws/stream")
async def ws_stream(ws: WebSocket):
    # Query params per connection
    qp = ws.query_params
    reflect = float(qp.get("reflectiveness", settings.reflectiveness))
    create = float(qp.get("creativity", settings.creativity))
    debug_meta = qp.get("debug_meta", "false").lower() in ("1","true","yes","on")
    await stream_loop(ws, reflect, create, debug_meta)
