from __future__ import annotations
import random, re, time
from typing import List, Dict, Any, Optional, Tuple
from models import Persona, Event, Post
from cognition import build_scratchpad
from scorer import score_temporal, score_voice, score_consistency, composite_score

FEATURES_BY_ERA = {
    "1914-08": {"hashtags": False, "retweet_prefix": "RT", "quote_tweet": False, "max_chars": 140}
}

BANNED = {"selfie","podcast","smartphone","wifi","streaming","hashtag","AI","DM","algorithm","crypto","blockchain","influencer","meme","lol","emoji"}

def load_lexicon(path: str) -> set[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return set(w.strip().lower() for w in f if w.strip())
    except Exception:
        return set()

def tokens_in_lexicon_ratio(text: str, lexicon: set[str]) -> float:
    tokens = [re.sub(r"[^\w']","",t).lower() for t in text.split()]
    words = [t for t in tokens if t]
    if not words: return 1.0
    ok = 0
    for w in words:
        if w in BANNED: continue
        if not w.isalpha(): 
            ok += 1
        elif (not lexicon) or (w in lexicon) or len(w) <= 6:
            ok += 1
    return ok/len(words)

def render_public(persona: Persona, ev: Optional[Event], scratch: Dict[str,Any], features: Dict[str,Any], lexicon: set[str]) -> str:
    fragments = []
    if ev:
        openers = [
            f"{ev.title}.",
            f"News from {ev.region}: {ev.title.lower()}.",
            f"{ev.summary}"
        ]
        fragments.append(random.choice(openers))
    else:
        musings = [
            "The office is hushed this morning.",
            "Queues at the post; whispers everywhere.",
            "Wireless carries grave reports.",
            "Factory floor abuzz; lads speak of enlistment."
        ]
        fragments.append(random.choice(musings))
    # self reference
    if scratch.get("self_reference"):
        sr = ["I fear","I wonder","It seems to me","I reckon","I confess"]
        fragments.append(random.choice(sr))
    # feeling colour
    colours = {
        "anxious": ["God save us.","One prays common sense shall prevail.","Best keep our heads."],
        "resolute": ["Steady on.","To work, then.","Let us do our part."],
        "uncertain": ["The gazette makes for stern reading.","Neighbours whisper of bills and trains."]
    }
    fset = colours.get(scratch.get("feeling","uncertain"), colours["uncertain"])
    if random.random() < 0.7:
        fragments.append(random.choice(fset))
    text = " ".join(fragments)
    # gate lexicon & banned
    def acceptable(token: str) -> bool:
        lt = token.lower().strip(".,;:!?—-")
        if lt in BANNED: return False
        return True
    tokens = text.split()
    tokens = [t for t in tokens if acceptable(t)]
    text = " ".join(tokens)
    max_chars = features.get("max_chars", 140)
    if len(text) > max_chars:
        text = text[:max_chars-1] + "…"
    return text

def two_pass_generate(persona: Persona, era: str, now_iso: str, ev: Optional[Event], lexicon: set[str], reflectiveness: float, creativity: float, include_meta: bool=False) -> Optional[Post]:
    features = FEATURES_BY_ERA.get(era, FEATURES_BY_ERA["1914-08"]).copy()
    # Pass 1: build scratchpad
    scratch = build_scratchpad(persona, ev, reflectiveness, creativity)
    # Pass 2: render candidate
    text = render_public(persona, ev, scratch, features, lexicon)
    # Score
    tscore = score_temporal(ev, era)
    vscore = score_voice(tokens_in_lexicon_ratio(text, lexicon))
    cscore = score_consistency(persona, text)
    final = composite_score(tscore, vscore, cscore, scratch.get("risk",0.0))
    if scratch["intent"] == "refrain" and final < 0.75:
        return None
    grounding = []
    if ev:
        grounding.append({"event_id": ev.id, "title": ev.title, "citations": ev.citations})
    meta = {"scratchpad": scratch, "scores": {"temporal": round(tscore,2), "voice": round(vscore,2), "consistency": round(cscore,2), "final": round(final,2)} } if include_meta else None
    return Post(
        id=f"t_{int(time.time()*1000)}_{random.randint(100,999)}",
        persona_id=persona.id,
        handle=persona.handle,
        timestamp=now_iso,
        text=text,
        features={"retweets": 0, "replies": 0, "quotes": 0, **features},
        grounding=grounding,
        meta=meta
    )
