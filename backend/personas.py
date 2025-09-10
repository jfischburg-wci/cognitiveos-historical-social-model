from __future__ import annotations
import random, string
from typing import List, Dict
from models import Persona

FIRST = ["Arthur","Beatrice","Cecil","Dorothy","Edmund","Florence","George","Harold","Irene","James","Katherine","Leonard","Mabel","Nora","Oswald","Phoebe","Quentin","Rose","Stanley","Trudy","Ursula","Victor","Winifred","Yvonne"]
LAST = ["Abbott","Baker","Cartwright","Dalton","Ellis","Foster","Gibson","Harris","Ingram","Jenkins","Kensington","Lyons","Morris","Nolan","Osborne","Parker","Quince","Rowley","Stephens","Turner","Underhill","Vickers","Watson","Yorke"]
OCC = ["clerk","teacher","journalist","shopkeeper","porter","seamstress","student","banker","factory worker","soldier","nurse"]
REGIONS = ["Europe-West","Europe-Central","Europe-Balkans","Europe-North","Europe-South"]
TOPICS = ["war","imperialism","mobilisation","alliances"]

def _handle(name: str) -> str:
    base = ''.join(ch for ch in name.lower() if ch.isalpha())
    suffix = ''.join(random.choice(string.ascii_lowercase) for _ in range(3))
    return f"{base}_{suffix}"

def sample_personas(n: int, era: str) -> List[Persona]:
    personas: List[Persona] = []
    for i in range(n):
        name = f"{random.choice(FIRST)} {random.choice(LAST)}"
        handle = _handle(name)
        region = random.choice(REGIONS)
        occupation = random.choice(OCC)
        alignment = {
            "war": random.uniform(-1, 1),
            "imperialism": random.uniform(-1, 1),
            "mobilisation": random.uniform(-1, 1),
            "alliances": random.uniform(-1, 1)
        }
        voice = {"formality": round(random.uniform(0.4, 0.9), 2), "dialect": "EN_1910s"}
        cog = {"reflectiveness": round(random.uniform(0.3, 0.8), 2),
               "certainty": round(random.uniform(0.3, 0.8), 2),
               "irony": round(random.uniform(0.0, 0.3), 2),
               "risk_appetite": round(random.uniform(0.2, 0.7), 2)}
        personas.append(Persona(
            id=f"p_{i:04d}", handle=handle, era=era, region=region,
            occupation=occupation, alignment=alignment, voice=voice,
            cognitive_style=cog
        ))
    # naive following network: each follows ~sqrt(n) others with region bias
    per = max(2, int(n ** 0.5))
    by_region: Dict[str, List[Persona]] = {}
    for p in personas:
        by_region.setdefault(p.region, []).append(p)
    for p in personas:
        pool = by_region[p.region][:] + personas
        pool = [q for q in pool if q.id != p.id]
        follows = random.sample(pool, k=min(per, len(pool)))
        p.following = [q.id for q in follows]
    # followers reverse
    id2p = {p.id: p for p in personas}
    for p in personas:
        for fid in p.following:
            id2p[fid].followers.append(p.id)
    return personas
