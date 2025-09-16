<script>
  import { createEventDispatcher, onMount, onDestroy } from 'svelte';
  import spec from './rig/corvid_v1.json';
  import constraints from './rig/constraints.json';

  // Props
  export let src = '/corvid_crow_anim_v9.svg';
  export let reduceMotion = false; // respected below

  // State
  const dispatch = createEventDispatcher();
  let host, svg;
  const activeAnims = new Set();
  const boneRanges = new Map(); // id -> [min,max] for pitch

  function track(anim){
    if (!anim) return anim;
    try {
      activeAnims.add(anim);
      anim.onfinish = () => activeAnims.delete(anim);
      anim.oncancel = () => activeAnims.delete(anim);
    } catch {}
    return anim;
  }

  // Constraint helpers sourced from skeleton spec
  const clampAngle = (id, deg, actionName='') => {
    const base = boneRanges.get(id);
    const actionRange = (() => {
      try { return constraints?.actions?.[actionName]?.pitch?.[id]; } catch { return null; }
    })();
    const r = actionRange || base;
    if (!r || !Array.isArray(r) || r.length < 2) return deg;
    return Math.max(r[0], Math.min(r[1], deg));
  };

  function clampTransformStr(id, s, actionName=''){
    if (!s) return s;
    return s.replace(/rotate\((-?\d+(?:\.\d+)?)deg\)/g, (_m, a) => `rotate(${clampAngle(id, parseFloat(a), actionName)}deg)`);
  }

  function animateBone(elId, boneId, keyframes, options, actionName=''){
    const el = svg?.getElementById(elId);
    if (!el) return null;
    const adj = (keyframes || []).map(k => {
      const obj = { ...k };
      if (obj.transform) obj.transform = clampTransformStr(boneId, obj.transform, actionName);
      return obj;
    });
    return track(el.animate(adj, options));
  }

  /* -------------------------------------------------------------
     Utilities
  ------------------------------------------------------------- */

  // Ensure eyelid group exists (some exports split into upper/lower only)
  function ensureIds() {
    if (!svg) return;
    const up = svg.getElementById('EyelidUpper');
    const lo = svg.getElementById('EyelidLower');
    if (up && lo && !svg.getElementById('Eyelids')) {
      const g = document.createElementNS('http://www.w3.org/2000/svg','g');
      g.setAttribute('id','Eyelids');
      up.parentNode.insertBefore(g, up);
      g.appendChild(up); g.appendChild(lo);
    }
  }

  // Create HeadSkull (wrap #Head only) and NeckUpper (wrap skull + beaks)
  function ensureHeadGroups() {
    if (!svg) return;
    const crow = svg.getElementById('Crow');
    if (!crow) return;

    // Split legacy HeadUpper (Head + BeakUpper) into HeadSkull + BeakUpper siblings
    const legacy = svg.getElementById('HeadUpper');
    if (legacy) {
      const head = legacy.querySelector('#Head');
      const bu   = legacy.querySelector('#BeakUpper');
      if (head && !svg.getElementById('HeadSkull')) {
        const skull = document.createElementNS('http://www.w3.org/2000/svg','g');
        skull.setAttribute('id','HeadSkull');
        skull.setAttribute('class','part headSkull');
        legacy.parentNode.insertBefore(skull, legacy);
        legacy.removeChild(head); skull.appendChild(head);
      }
      if (bu) legacy.parentNode.insertBefore(bu, legacy);
      if (!legacy.firstChild) legacy.parentNode.removeChild(legacy);
    } else {
      // Otherwise just wrap Head in HeadSkull
      const head = svg.getElementById('Head');
      if (head && !svg.getElementById('HeadSkull')) {
        const skull = document.createElementNS('http://www.w3.org/2000/svg','g');
        skull.setAttribute('id','HeadSkull');
        skull.setAttribute('class','part headSkull');
        head.parentNode.insertBefore(skull, head);
        head.parentNode.removeChild(head);
        skull.appendChild(head);
      }
    }

    // Create NeckUpper wrapper to move the entire head assembly together
    if (!svg.getElementById('NeckUpper')) {
      const skull = svg.getElementById('HeadSkull');
      const bu = svg.getElementById('BeakUpper');
      const bl = svg.getElementById('BeakLower');
      const nodes = [skull, bu, bl].filter(Boolean);
      if (nodes.length) {
        const neckU = document.createElementNS('http://www.w3.org/2000/svg','g');
        neckU.setAttribute('id','NeckUpper');
        neckU.setAttribute('class','part neckUpper');
        // Insert before the earliest node by document order
        const first = nodes.reduce((a,b)=> (a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING) ? a : b);
        first.parentNode.insertBefore(neckU, first);
        // Move nodes into neckU preserving current order in DOM
        [skull, bu, bl].forEach(n => { if (n) neckU.appendChild(n); });
      }
    }
  }

  // Wrap Head + BeakUpper into a single group so they can rotate from a common jaw hinge
  function ensureHeadUpperGroup() {
    if (!svg) return;
    const head = svg.getElementById('Head');
    const bu   = svg.getElementById('BeakUpper');
    if (!head || !bu) return;
    if (svg.getElementById('HeadUpper')) return; // already wrapped

    const headSkull = svg.getElementById('HeadSkull');
    const neckUpper = svg.getElementById('NeckUpper');
    const modernLayout = headSkull && neckUpper && head.parentNode === headSkull && bu.parentNode === neckUpper;
    if (modernLayout) return; // new segmented SVG already provides dedicated wrappers

    const parent = head.parentNode; // expected Crow group
    const group = document.createElementNS('http://www.w3.org/2000/svg','g');
    group.setAttribute('id','HeadUpper');
    group.setAttribute('class','part headUpper');
    // Insert before the earlier of head/beakUpper, then move both inside
    const before = (head.compareDocumentPosition(bu) & Node.DOCUMENT_POSITION_FOLLOWING) ? head : bu;
    parent.insertBefore(group, before);
    parent.removeChild(head); group.appendChild(head);
    parent.removeChild(bu);   group.appendChild(bu);
  }

  // Inject fallback keyframes/classes if the SVG didn’t ship with them
  function ensureAnimationStyle() {
    if (!svg) return;
    const has = Array.from(svg.querySelectorAll('style')).some(s => s.textContent.includes('animate-headBob'));
    if (has) return;
    const css = `
      @keyframes headBob {0%,100%{transform:translateY(0)}50%{transform:translateY(6px)}}
      @keyframes blink {0%,92%,100%{transform:scaleY(1)}94%{transform:scaleY(.15)}96%{transform:scaleY(1)}}
      @keyframes preen {0%,100%{transform:rotate(0)}40%{transform:rotate(-4deg)}60%{transform:rotate(3deg)}}
      @keyframes hop {0%,100%{transform:translateY(0)}30%{transform:translateY(-20px)}60%{transform:translateY(-8px)}}
      @keyframes beakOpen {0%,100%{transform:rotate(0)}30%{transform:rotate(-12deg)}}
      @keyframes beakLower {0%,100%{transform:rotate(0)}30%{transform:rotate(14deg)}}
      /* walking fallback */
      @keyframes walk { 0%{transform:translateX(0)} 25%{transform:translateX(8px)} 50%{transform:translateX(16px)} 75%{transform:translateX(24px)} 100%{transform:translateX(32px)} }
      @keyframes walkHeadBob { 0%,100%{transform:translateY(0)} 50%{transform:translateY(4px)} }
      .animate-headBob #Head{animation:headBob 1.2s ease-in-out 1}
      .animate-blink #EyelidUpper,.animate-blink #EyelidLower{transform-origin:50% 50%;animation:blink .24s 1}
      .animate-preen #Wing{transform-origin:33% 36%;animation:preen 2.4s ease-in-out 1}
      .animate-hop #Crow{animation:hop .9s cubic-bezier(.3,.6,.3,1) 1}
      .animate-caw #BeakUpper{transform-origin:60% 23%;animation:beakOpen .6s 1}
      .animate-caw #BeakLower{transform-origin:61% 26%;animation:beakLower .6s 1}
      .animate-walk #Crow{animation:walk .6s steps(2,end) 1}
      .loop-walk #Crow{animation:walk .6s steps(2,end) infinite}
      .loop-walk #Head{animation:walkHeadBob .3s ease-in-out infinite}
    `;
    const style = document.createElementNS('http://www.w3.org/2000/svg','style');
    style.textContent = css;
    svg.insertBefore(style, svg.firstChild);
  }

  // Build a lightweight skeleton per spec: ensure runtime wrappers and pivots
  function ensureSkeleton(){
    if (!svg || !spec || !Array.isArray(spec.bones)) return;
    const ns = 'http://www.w3.org/2000/svg';
    const vb = svg.viewBox?.baseVal
      || (
        (svg.width && svg.width.baseVal && svg.height && svg.height.baseVal)
          ? { x: 0, y: 0, width: svg.width.baseVal.value, height: svg.height.baseVal.value }
          : (() => {
              try {
                const box = typeof svg.getBBox === 'function' ? svg.getBBox() : null;
                if (box) return { x: box.x, y: box.y, width: box.width, height: box.height };
              } catch {}
              return { x: 0, y: 0, width: 0, height: 0 };
            })()
        );

    const toPx = (p) => p?.px ? { x:p.px[0], y:p.px[1] } : (p?.rel ? { x: vb.width*p.rel[0], y: vb.height*p.rel[1] } : null);
    const byId = (id) => svg.getElementById(id);
    const ensureGroup = (id, aliasId) => {
      let el = byId(id);
      if (el) return el;
      const g = document.createElementNS(ns,'g'); g.setAttribute('id', id); g.setAttribute('class','bone');
      const alias = aliasId ? byId(aliasId) : null;
      if (alias && alias.parentNode) { alias.replaceWith(g); g.appendChild(alias); }
      else { (byId('Crow') || svg).appendChild(g); }
      return g;
    };

    // Iterate a few passes so parents exist before children
    const pending = new Set(spec.bones.map(b => b.id));
    for (let pass=0; pass<3 && pending.size; pass++) {
      for (const b of spec.bones) {
        if (!pending.has(b.id)) continue;
        if (b.parent && !byId(b.parent)) continue;
        const el = ensureGroup(b.id, b.alias);
        const piv = toPx(b.pivot);
        if (el && piv) el.style.transformOrigin = `${piv.x}px ${piv.y}px`;
        if (b?.dof?.pitch) boneRanges.set(b.id, b.dof.pitch);
        pending.delete(b.id);
      }
    }

    // Perf hint
    spec.bones.forEach(b => { const el = byId(b.id); if (el) el.style.willChange = 'transform'; });

    // Apply artist constraints (overrides spec if present)
    try {
      if (constraints?.pitch) {
        Object.entries(constraints.pitch).forEach(([id, range]) => {
          if (Array.isArray(range) && range.length === 2) boneRanges.set(id, range);
        });
      }
    } catch {}
  }

  // Developer overlay: draws bone pivots and parent-child links.
  function drawDevOverlay(){
    if (!svg || !spec || !Array.isArray(spec.bones)) return;
    const ns = 'http://www.w3.org/2000/svg';
    // Remove existing
    const existing = svg.getElementById('DevOverlay');
    if (existing && existing.parentNode) existing.parentNode.removeChild(existing);
    const vb = svg.viewBox?.baseVal
      || ((svg.width && svg.width.baseVal && svg.height && svg.height.baseVal)
          ? { x:0,y:0,width: svg.width.baseVal.value, height: svg.height.baseVal.value }
          : { x:0,y:0,width:0,height:0 });
    const toPx = (p) => p?.px ? { x:p.px[0], y:p.px[1] } : (p?.rel ? { x: vb.width*p.rel[0], y: vb.height*p.rel[1] } : null);
    const pivots = new Map();
    spec.bones.forEach(b => { const p = toPx(b.pivot); if (p) pivots.set(b.id, p); });
    const g = document.createElementNS(ns,'g');
    g.setAttribute('id','DevOverlay');
    g.setAttribute('pointer-events','none');
    g.setAttribute('style','mix-blend-mode:screen');
    // Lines first
    spec.bones.forEach(b => {
      if (!b.parent) return;
      const a = pivots.get(b.parent); const c = pivots.get(b.id);
      if (!a || !c) return;
      const line = document.createElementNS(ns,'line');
      line.setAttribute('x1', a.x); line.setAttribute('y1', a.y);
      line.setAttribute('x2', c.x); line.setAttribute('y2', c.y);
      line.setAttribute('stroke', 'rgba(130,247,255,0.35)');
      line.setAttribute('stroke-width','1.2');
      g.appendChild(line);
    });
    // Pivots
    spec.bones.forEach(b => {
      const p = pivots.get(b.id); if (!p) return;
      const circ = document.createElementNS(ns,'circle');
      circ.setAttribute('cx', p.x); circ.setAttribute('cy', p.y); circ.setAttribute('r','3');
      circ.setAttribute('fill','rgba(130,247,255,0.8)');
      const txt = document.createElementNS(ns,'text');
      txt.textContent = b.id;
      txt.setAttribute('x', String(p.x + 5)); txt.setAttribute('y', String(p.y - 5));
      txt.setAttribute('font-size','9'); txt.setAttribute('fill','rgba(130,247,255,0.8)');
      txt.setAttribute('id', `DevTxt-${b.id}`);
      g.appendChild(circ); g.appendChild(txt);
    });
    svg.appendChild(g);

    // Start telemetry updates (angles)
    startOverlayTelemetry();
  }

  function devOverlayEnabled(){
    try {
      if (import.meta?.env?.VITE_CORVID_DEV_OVERLAY === '1') return true;
      const q = new URLSearchParams(window.location.search);
      if (q.get('dev') === '1' || q.get('overlay') === '1') return true;
      if (localStorage.getItem('corvidDevOverlay') === '1') return true;
    } catch {}
    return false;
  }

  let devOverlayRaf = null;
  function startOverlayTelemetry(){
    cancelOverlayTelemetry();
    const tick = () => {
      try {
        spec?.bones?.forEach?.((b) => {
          const el = svg?.getElementById(b.id) || (b.alias && svg?.getElementById(b.alias));
          const label = svg?.getElementById(`DevTxt-${b.id}`);
          if (!el || !label) return;
          const cs = getComputedStyle(el);
          const t = cs.transform;
          let deg = 0;
          if (t && t !== 'none') {
            try {
              const m = new DOMMatrixReadOnly(t);
              deg = Math.atan2(m.b, m.a) * 180 / Math.PI;
            } catch {}
          }
          const base = boneRanges.get(b.id);
          const rtxt = base ? ` [${base[0]}..${base[1]}]` : '';
          label.textContent = `${b.id} ${deg.toFixed(1)}°${rtxt}`;
        });
      } catch {}
      devOverlayRaf = requestAnimationFrame(tick);
    };
    devOverlayRaf = requestAnimationFrame(tick);
  }

  function cancelOverlayTelemetry(){
    if (devOverlayRaf) cancelAnimationFrame(devOverlayRaf);
    devOverlayRaf = null;
  }

  // Slightly dilate a mask so adjacent parts overlap (prevents AA slits)
  function dilateMask(maskId, radiusPx) {
    const ns = 'http://www.w3.org/2000/svg';
    const m = svg.getElementById(maskId);
    if (!m) return;

    let defs = svg.querySelector('defs');
    if (!defs) { defs = document.createElementNS(ns,'defs'); svg.insertBefore(defs, svg.firstChild); }

    const fid = `exp-${maskId}`;
    if (!svg.getElementById(fid)) {
      const f = document.createElementNS(ns,'filter');
      f.setAttribute('id', fid);
      f.setAttribute('filterUnits','userSpaceOnUse');
      f.setAttribute('primitiveUnits','userSpaceOnUse');
      // huge bounds so the filter never clips
      f.setAttribute('x','-10000'); f.setAttribute('y','-10000');
      f.setAttribute('width','20000'); f.setAttribute('height','20000');

      const morph = document.createElementNS(ns,'feMorphology');
      morph.setAttribute('operator','dilate');
      morph.setAttribute('radius', String(radiusPx));

      const blur = document.createElementNS(ns,'feGaussianBlur');
      blur.setAttribute('stdDeviation','0.2');

      f.appendChild(morph);
      f.appendChild(blur);
      defs.appendChild(f);
    }

    const wrap = document.createElementNS(ns,'g');
    wrap.setAttribute('filter', `url(#${fid})`);
    while (m.firstChild) wrap.appendChild(m.firstChild);
    m.appendChild(wrap);
  }

  // Hard clip rectangles for beaks so the tip never clips
  function clipBeak(id, x0, y0, x1, y1) {
    const ns='http://www.w3.org/2000/svg';
    const g = svg.getElementById(id); if (!g) return;
    let defs = svg.querySelector('defs'); if (!defs) { defs = document.createElementNS(ns,'defs'); svg.insertBefore(defs, svg.firstChild); }
    const cpid = `cp-${id}`;
    if (!svg.getElementById(cpid)) {
      const cp = document.createElementNS(ns,'clipPath'); cp.setAttribute('id', cpid);
      const r  = document.createElementNS(ns,'rect');
      r.setAttribute('x', x0); r.setAttribute('y', y0);
      r.setAttribute('width', x1 - x0); r.setAttribute('height', y1 - y0);
      cp.appendChild(r); defs.appendChild(cp);
    }
    g.setAttribute('clip-path', `url(#${cpid})`);
  }

  // Set anatomical transform origins (px) for natural motion
  function prepareRig() {
    const setOrigin = (id, x, y) => {
      const el = svg.getElementById(id);
      if (el) el.style.transformOrigin = `${x}px ${y}px`;
      return el;
    };
    const vb = svg.viewBox.baseVal || { x:0, y:0, width: svg.width.baseVal.value, height: svg.height.baseVal.value };
    const HEAD = { x: vb.width*0.50, y: vb.height*0.20 };
    const WING = { x: vb.width*0.33, y: vb.height*0.36 };
    const WINGA= { x: WING.x,         y: WING.y };
    const WINGB= { x: vb.width*0.40, y: vb.height*0.38 };
    const WINGC= { x: vb.width*0.48, y: vb.height*0.41 };
    const NECKB= { x: vb.width*0.44, y: vb.height*0.30 };
    const NECKM= { x: vb.width*0.44, y: vb.height*0.26 };
    const BU   = { x: vb.width*0.60, y: vb.height*0.23 };
    const BL   = { x: vb.width*0.61, y: vb.height*0.26 };
    const EYE  = { x: vb.width*0.523, y: vb.height*0.205 };
    const TAIL = { x: vb.width*0.19, y: vb.height*0.62 };
    const LFOOT= { x: vb.width*0.37, y: vb.height*0.82 };
    const RFOOT= { x: vb.width*0.49, y: vb.height*0.82 };

    setOrigin('Head', HEAD.x, HEAD.y);
    // Legacy hints (skeleton sets proper pivots already)
    setOrigin('HeadSkull', BU.x, BU.y);
    setOrigin('SkullTop', BU.x, BU.y);
    setOrigin('NeckBase', NECKB.x, NECKB.y);
    setOrigin('Neck', NECKB.x, NECKB.y);
    setOrigin('NeckUpper', NECKM.x, NECKM.y);
    setOrigin('HeadUpper', BU.x, BU.y);
    setOrigin('Wing',  WING.x,  WING.y);
    setOrigin('WingA', WINGA.x, WINGA.y);
    setOrigin('WingB', WINGB.x, WINGB.y);
    setOrigin('WingC', WINGC.x, WINGC.y);
    setOrigin('NeckMid', NECKM.x, NECKM.y);
    setOrigin('BeakUpper', BU.x, BU.y);
    setOrigin('BeakLower', BL.x, BL.y);
    setOrigin('EyelidUpper', EYE.x, EYE.y);
    setOrigin('EyelidLower', EYE.x, EYE.y + 6);
    ['TailA','TailB','TailC','TailD'].forEach(id => setOrigin(id, TAIL.x, TAIL.y));
    setOrigin('FootLeft',  LFOOT.x, LFOOT.y);
    setOrigin('FootRight', RFOOT.x, RFOOT.y);

    // Hint to engines that these nodes will animate transforms
    ['Crow','Head','HeadSkull','SkullTop','NeckBase','NeckUpper','HeadUpper','NeckMid','Shoulder','Elbow','Wrist','Primaries','TailBase','HipLeft','KneeLeft','AnkleLeft','ToesLeft','HipRight','KneeRight','AnkleRight','ToesRight','Wing','WingA','WingB','WingC','BeakUpper','BeakLower','EyelidUpper','EyelidLower','TailA','TailB','TailC','TailD','Legs','Feet','FootLeft','FootRight']
      .forEach(id => { const el = svg.getElementById(id); if (el) el.style.willChange = 'transform'; });
  }

  /* -------------------------------------------------------------
     WAAPI animation functions (anatomical)
  ------------------------------------------------------------- */

  function blink(){
    const up = svg.getElementById('EyelidUpper');
    const lo = svg.getElementById('EyelidLower');
    if (!up || !lo) return Promise.resolve();
    const upUnder = svg.getElementById('EyelidUpperUnderlay');
    const loUnder = svg.getElementById('EyelidLowerUnderlay');

    // Ensure eyelids only: in-head, clipped, and animated via translate toward center
    up.style.transformBox = 'fill-box';
    lo.style.transformBox = 'fill-box';
    up.style.transform = 'translateY(0px)';
    lo.style.transform = 'translateY(0px)';
    // Don't rely on scale; slide lids toward the eye line and slightly overlap to avoid a sliver
    up.style.opacity = '1';
    lo.style.opacity = '1';
    if (upUnder) upUnder.style.opacity = '1';
    if (loUnder) loUnder.style.opacity = '1';

    // Compute travel based on eyelid geometry so exports with different scaling still close cleanly
    const box = (node) => {
      try { return typeof node.getBBox === 'function' ? node.getBBox() : null; } catch { return null; }
    };
    const upBox = box(up);
    const loBox = box(lo);
    const gap = (upBox && loBox) ? Math.max(0, loBox.y - (upBox.y + upBox.height)) : 28;
    const baseTravel = gap > 0 ? gap / 2 : 14;
    const overlap = Math.min(2.4, Math.max(0.8, baseTravel * 0.2));
    const upTravel = baseTravel + overlap;
    const loTravel = baseTravel + overlap;

    const kfU = [
      { transform: 'translateY(0px)' },
      { transform: `translateY(${upTravel}px)` },
      { transform: 'translateY(0px)' }
    ];
    const kfL = [
      { transform: 'translateY(0px)' },
      { transform: `translateY(${-loTravel}px)` },
      { transform: 'translateY(0px)' }
    ];

    // Fast close, slight hold, natural open
    const quick = 160; // ms (one-blink)
    const slow  = 230; // ms (double-blink second pass)
    const ease  = 'cubic-bezier(.4,.0,.2,1)'; // standard material-ish ease

    const aU1 = track(up.animate(kfU, { duration: quick, easing: ease, fill: 'none' }));
    const aL1 = track(lo.animate(kfL, { duration: quick, easing: ease, fill: 'none' }));

    // Occasional double-blink (~18%) with a short pause
    const maybeSecond = Math.random() < 0.18;

    return Promise.all([aU1.finished, aL1.finished]).then(async () => {
      if (maybeSecond) {
        await new Promise(r => setTimeout(r, 70));
        const aU2 = track(up.animate(kfU, { duration: slow, easing: ease, fill: 'none' }));
        const aL2 = track(lo.animate(kfL, { duration: slow, easing: ease, fill: 'none' }));
        await Promise.all([aU2.finished, aL2.finished]);
      }
      // Hide eyelids again (neutral)
      up.style.opacity = '0';
      lo.style.opacity = '0';
      if (upUnder) upUnder.style.opacity = '0';
      if (loUnder) loUnder.style.opacity = '0';
      // Clear any residual transform to ensure clean neutral state
      up.style.transform = '';
      lo.style.transform = '';
      dispatch('interact');
    });
  }

  function headBob(){
    const head = svg.getElementById('Head');
    const skull = svg.getElementById('HeadSkull');
    const skullTop = svg.getElementById('SkullTop');
    const neckB = svg.getElementById('NeckBase');
    const neckm = svg.getElementById('NeckMid');
    const neckU = svg.getElementById('NeckUpper');
    const tailB = svg.getElementById('TailBase');
    if (!head) return Promise.resolve();
    const dur = 900;
    const ease = 'cubic-bezier(.3,.6,.3,1)';
    const promises = [];
    promises.push(head.animate(
      [
        { transform:'translateY(0px) rotate(0deg)' },
        { transform:'translateY(6px) rotate(-1deg)' },
        { transform:'translateY(0px) rotate(0deg)' }
      ],
      { duration: dur, easing: ease, fill: 'none' }
    ).finished);
    if (neckB) promises.push(animateBone('NeckBase','NeckBase',[
      { transform:'rotate(0deg)' },
      { transform:'rotate(-2deg)' },
      { transform:'rotate(0deg)' }
    ], { duration: dur, easing: ease, fill:'none' }, 'headBob')?.finished ?? Promise.resolve());
    if (neckm) promises.push(animateBone('NeckMid','NeckMid',[
      { transform:'rotate(0deg)' },
      { transform:'rotate(-3deg)' },
      { transform:'rotate(0deg)' }
    ], { duration: dur, easing: ease, fill:'none' }, 'headBob')?.finished ?? Promise.resolve());
    if (neckU) promises.push(animateBone('NeckUpper','NeckUpper',[
      { transform:'rotate(0deg)' },
      { transform:'rotate(-4.5deg)' },
      { transform:'rotate(0deg)' }
    ], { duration: dur, easing: ease, fill:'none' }, 'headBob')?.finished ?? Promise.resolve());
    if (skull) promises.push(animateBone(skull.id || 'HeadSkull','HeadSkull',[
      { transform:'rotate(0deg)' },
      { transform:'rotate(-4deg)' },
      { transform:'rotate(0deg)' }
    ], { duration: dur, easing: ease, fill:'none' }, 'headBob')?.finished ?? Promise.resolve());
    if (skullTop) promises.push(animateBone('SkullTop','SkullTop',[
      { transform:'rotate(0deg)' },
      { transform:'rotate(-5.5deg)' },
      { transform:'rotate(0deg)' }
    ], { duration: dur, easing: ease, fill:'none' }, 'headBob')?.finished ?? Promise.resolve());
    if (tailB) promises.push(tailB.animate(
      [ { transform:'rotate(0deg)' }, { transform:'rotate(2deg)' }, { transform:'rotate(0deg)' } ],
      { duration: dur, easing: ease, fill:'none' }
    ).finished);
    return Promise.all(promises).then(()=>{});
  }

  function preen(){
    // Prefer articulated bones if present
    const shoulder = svg.getElementById('Shoulder') || svg.getElementById('Wing');
    const elbow    = svg.getElementById('Elbow')    || svg.getElementById('WingB');
    const wrist    = svg.getElementById('Wrist')    || svg.getElementById('WingC');
    const prim     = svg.getElementById('Primaries');
    const skull    = svg.getElementById('HeadSkull');
    const skullTop = svg.getElementById('SkullTop');
    const neckU    = svg.getElementById('NeckUpper');
    const tails = ['TailA','TailB','TailC','TailD'].map(id=>svg.getElementById(id)).filter(Boolean);
    const tailB = svg.getElementById('TailBase');
    if (!shoulder) return Promise.resolve();
    const dur = 1600;
    const ease = 'ease-in-out';
    const promises = [];
    promises.push(animateBone(shoulder?.id || 'Shoulder', 'Shoulder', [
      { transform:'rotate(0deg)' },
      { transform:'rotate(-6deg)' },
      { transform:'rotate(3deg)'  },
      { transform:'rotate(0deg)' }
    ], { duration: dur, easing:ease, fill:'none' }, 'preen')?.finished ?? Promise.resolve());
    if (elbow) promises.push(animateBone(elbow.id, 'Elbow', [
      { transform:'rotate(0deg)' }, { transform:'rotate(-3deg)' }, { transform:'rotate(1.5deg)' }, { transform:'rotate(0deg)' }
    ], { duration: dur, delay: 100, easing:ease, fill:'none' }, 'preen')?.finished ?? Promise.resolve());
    if (wrist) promises.push(animateBone(wrist.id, 'Wrist', [
      { transform:'rotate(0deg)' }, { transform:'rotate(-2deg)' }, { transform:'rotate(1deg)' }, { transform:'rotate(0deg)' }
    ], { duration: dur, delay: 140, easing:ease, fill:'none' }, 'preen')?.finished ?? Promise.resolve());
    if (prim) promises.push(animateBone(prim.id, 'Primaries', [
      { transform:'rotate(0deg)' }, { transform:'rotate(-1.2deg)' }, { transform:'rotate(0.6deg)' }, { transform:'rotate(0deg)' }
    ], { duration: dur, delay: 180, easing:ease, fill:'none' }, 'preen')?.finished ?? Promise.resolve());
    if (neckU) promises.push(animateBone('NeckUpper','NeckUpper',[
      { transform:'rotate(0deg)' }, { transform:'rotate(-4deg)' }, { transform:'rotate(-1deg)' }, { transform:'rotate(0deg)' }
    ], { duration: dur, delay: 80, easing:ease, fill:'none' }, 'preen')?.finished ?? Promise.resolve());
    if (skull) promises.push(animateBone(skull.id || 'HeadSkull','HeadSkull',[
      { transform:'rotate(0deg)' }, { transform:'rotate(-4deg)' }, { transform:'rotate(-1deg)' }, { transform:'rotate(0deg)' }
    ], { duration: dur, delay: 120, easing:ease, fill:'none' }, 'preen')?.finished ?? Promise.resolve());
    if (skullTop) promises.push(animateBone('SkullTop','SkullTop',[
      { transform:'rotate(0deg)' }, { transform:'rotate(-5deg)' }, { transform:'rotate(-1.5deg)' }, { transform:'rotate(0deg)' }
    ], { duration: dur, delay: 160, easing:ease, fill:'none' }, 'preen')?.finished ?? Promise.resolve());
    if (tailB) promises.push(tailB.animate(
      [{ transform:'rotate(0deg)' }, { transform:'rotate(2.4deg)' }, { transform:'rotate(0deg)' }],
      { duration: 1200, delay: 120, easing:ease, fill:'none' }
    ).finished);
    tails.forEach((t,i)=>{
      promises.push(t.animate(
        [{ transform:'rotate(0deg)' }, { transform:`rotate(${i%2?2:-2}deg)` }, { transform:'rotate(0deg)' }],
        { duration: 1200, delay: i*60, easing:ease, fill:'none' }
      ).finished);
    });
    return Promise.all(promises).then(()=>{});
  }

  function hop(){
    const crow  = svg.getElementById('Crow');
    const feet  = [svg.getElementById('FootLeft'), svg.getElementById('FootRight')].filter(Boolean);
    const shoulder = svg.getElementById('Shoulder') || svg.getElementById('Wing');
    const elbow    = svg.getElementById('Elbow')    || svg.getElementById('WingB');
    const wrist    = svg.getElementById('Wrist')    || svg.getElementById('WingC');
    const neckU    = svg.getElementById('NeckUpper') || svg.getElementById('NeckMid');
    const skull    = svg.getElementById('HeadSkull');
    const skullTop = svg.getElementById('SkullTop');
    const tailB    = svg.getElementById('TailBase');
    const tails    = ['TailA','TailB','TailC','TailD'].map(id=>svg.getElementById(id)).filter(Boolean);
    // Legs (prefer bones, fall back to legacy groups)
    const hipL  = svg.getElementById('HipLeft')   || svg.getElementById('LegLeft');
    const kneeL = svg.getElementById('KneeLeft')  || null;
    const anklL = svg.getElementById('AnkleLeft') || svg.getElementById('FootLeft');
    const toeL  = svg.getElementById('ToesLeft')  || svg.getElementById('FootLeft');
    const hipR  = svg.getElementById('HipRight')   || svg.getElementById('LegRight');
    const kneeR = svg.getElementById('KneeRight')  || null;
    const anklR = svg.getElementById('AnkleRight') || svg.getElementById('FootRight');
    const toeR  = svg.getElementById('ToesRight')  || svg.getElementById('FootRight');
    if (!crow) return Promise.resolve();
    const dur = 900;

    // Horizontal advance accumulator so successive hops move forward
    if (typeof hop.baseX !== 'number') hop.baseX = 0;
    const dx = 80; // visible forward motion per hop
    const x0 = hop.baseX;
    const x1 = x0 + dx;
    // Ensure baseline translation is applied before animating
    crow.style.transform = `translate(${x0}px, 0px)`;
    crow.animate(
      [
        { transform:`translate(${x0}px, 0px)` },
        { transform:`translate(${x0 + dx*0.5}px, -20px)` },
        { transform:`translate(${x1}px, -8px)` },
        { transform:`translate(${x1}px, 0px)` }
      ],
      { duration: dur, easing:'cubic-bezier(.3,.6,.3,1)', fill:'none' }
    ).finished.then(() => { hop.baseX = x1; crow.style.transform = `translate(${hop.baseX}px, 0px)`; }).catch(()=>{});
    feet.forEach(f => f.animate(
      [{ transform:'rotate(0deg)' }, { transform:'rotate(8deg)' }, { transform:'rotate(0deg)' }],
      { duration: 400, easing:'ease-out', fill:'none' }
    ));
    // Gentle, coordinated wing articulation to avoid rigid disconnects
    const wEase = 'cubic-bezier(.3,.6,.3,1)';
    if (shoulder) animateBone(shoulder.id, 'Shoulder', [
      { transform:'rotate(0deg)' }, { transform:'rotate(-6deg)' }, { transform:'rotate(-2deg)' }, { transform:'rotate(0deg)' }
    ], { duration: dur, easing: wEase, fill:'none' }, 'hop');
    if (elbow)    animateBone(elbow.id, 'Elbow', [
      { transform:'rotate(0deg)' }, { transform:'rotate(-4deg)' }, { transform:'rotate(-1.5deg)' }, { transform:'rotate(0deg)' }
    ], { duration: dur, delay: 70, easing: wEase, fill:'none' }, 'hop');
    if (wrist)    animateBone(wrist.id, 'Wrist', [
      { transform:'rotate(0deg)' }, { transform:'rotate(-3deg)' }, { transform:'rotate(-1deg)' }, { transform:'rotate(0deg)' }
    ], { duration: dur, delay: 100, easing: wEase, fill:'none' }, 'hop');
    if (neckU)    animateBone(neckU.id || 'NeckUpper', 'NeckUpper', [
      { transform:'rotate(0deg)' }, { transform:'rotate(-4deg)' }, { transform:'rotate(0deg)' }
    ], { duration: dur, delay: 90, easing: wEase, fill:'none' }, 'hop');
    if (skull)    animateBone(skull.id || 'HeadSkull', 'HeadSkull', [
      { transform:'rotate(0deg)' }, { transform:'rotate(-4deg)' }, { transform:'rotate(0deg)' }
    ], { duration: dur, delay: 110, easing: wEase, fill:'none' }, 'hop');
    if (skullTop) animateBone('SkullTop', 'SkullTop', [
      { transform:'rotate(0deg)' }, { transform:'rotate(-5deg)' }, { transform:'rotate(0deg)' }
    ], { duration: dur, delay: 110, easing: wEase, fill:'none' }, 'hop');
    if (tailB) tailB.animate(
      [{ transform:'rotate(0deg)' }, { transform:'rotate(3deg)' }, { transform:'rotate(0deg)' }],
      { duration: dur, delay: 60, easing: wEase, fill:'none' }
    );
    tails.forEach((t,i)=>{
      t.animate(
        [{ transform:'rotate(0deg)' }, { transform:`rotate(${i%2?1.6:-1.6}deg)` }, { transform:'rotate(0deg)' }],
        { duration: dur-200, delay: 60 + i*40, easing: wEase, fill:'none' }
      );
    });

    // Leg compression and toe curl during hop arc
    const legEase = 'cubic-bezier(.3,.6,.3,1)';
    const legKF = (h,k,a,t) => [
      { transform:'rotate(0deg)' },
      { transform:`rotate(${h}deg)` },
      { transform:'rotate(0deg)' }
    ];
    if (hipL)  animateBone(hipL.id,  'HipLeft',    [ { transform:'rotate(0deg)' }, { transform:'rotate(12deg)' }, { transform:'rotate(0deg)' } ], { duration: dur, easing: legEase, fill:'none' }, 'hop');
    if (kneeL) animateBone(kneeL.id, 'KneeLeft',   [ { transform:'rotate(0deg)' }, { transform:'rotate(24deg)' }, { transform:'rotate(0deg)' } ], { duration: dur, delay: 10, easing: legEase, fill:'none' }, 'hop');
    if (anklL) animateBone(anklL.id,'AnkleLeft',  [ { transform:'rotate(0deg)' }, { transform:'rotate(-10deg)' }, { transform:'rotate(0deg)' } ], { duration: dur, delay: 20, easing: legEase, fill:'none' }, 'hop');
    if (toeL)  animateBone(toeL.id, 'ToesLeft',   [ { transform:'rotate(0deg)' }, { transform:'rotate(10deg)' }, { transform:'rotate(0deg)' } ], { duration: dur, delay: 40, easing: legEase, fill:'none' }, 'hop');
    if (hipR)  animateBone(hipR.id,  'HipRight',   [ { transform:'rotate(0deg)' }, { transform:'rotate(12deg)' }, { transform:'rotate(0deg)' } ], { duration: dur, easing: legEase, fill:'none' }, 'hop');
    if (kneeR) animateBone(kneeR.id, 'KneeRight',  [ { transform:'rotate(0deg)' }, { transform:'rotate(24deg)' }, { transform:'rotate(0deg)' } ], { duration: dur, delay: 10, easing: legEase, fill:'none' }, 'hop');
    if (anklR) animateBone(anklR.id,'AnkleRight', [ { transform:'rotate(0deg)' }, { transform:'rotate(-10deg)' }, { transform:'rotate(0deg)' } ], { duration: dur, delay: 20, easing: legEase, fill:'none' }, 'hop');
    if (toeR)  animateBone(toeR.id, 'ToesRight',  [ { transform:'rotate(0deg)' }, { transform:'rotate(10deg)' }, { transform:'rotate(0deg)' } ], { duration: dur, delay: 40, easing: legEase, fill:'none' }, 'hop');
    dispatch('interact');
    return Promise.resolve();
  }

  function caw(){
    const skull = svg.getElementById('HeadSkull') || svg.getElementById('HeadUpper') || svg.getElementById('Head');
    const skullTop = svg.getElementById('SkullTop');
    const up    = svg.getElementById('BeakUpper');
    const lo    = svg.getElementById('BeakLower');
    const neckB = svg.getElementById('NeckBase');
    const neckU = svg.getElementById('NeckUpper') || svg.getElementById('NeckMid');
    if (!lo) return Promise.resolve();

    const durJaw = 210;
    const ease   = 'cubic-bezier(.2,.8,.2,1)';
    const headEase = 'cubic-bezier(.3,.6,.3,1)';
    const anims = [];
    if (neckB) anims.push(animateBone('NeckBase','NeckBase',[
      { transform:'rotate(0deg)' },
      { transform:'rotate(-4deg)' },
      { transform:'rotate(0deg)' }
    ], { duration: durJaw + 120, easing: headEase, fill:'none' }, 'caw')?.finished);
    if (neckU) anims.push(animateBone(neckU.id || 'NeckUpper', 'NeckUpper', [
      { transform:'translate(0px, 0px) rotate(0deg)' },
      { transform:'translate(2.2px, -4px) rotate(-8deg)' },
      { transform:'translate(0px, 0px) rotate(0deg)' }
    ], { duration: durJaw + 140, easing: headEase, fill:'none' }, 'caw')?.finished);
    if (skull) anims.push(animateBone(skull.id || 'HeadSkull', 'HeadSkull', [
      { transform:'rotate(0deg)' },
      { transform:'rotate(-9deg)' },
      { transform:'rotate(0deg)' }
    ], { duration: durJaw, easing: ease, fill:'none' }, 'caw')?.finished);
    if (skullTop) anims.push(animateBone('SkullTop', 'SkullTop', [
      { transform:'rotate(0deg)' },
      { transform:'rotate(-12deg)' },
      { transform:'rotate(0deg)' }
    ], { duration: durJaw, easing: ease, fill:'none' }, 'caw')?.finished);
    if (up) anims.push(animateBone(up.id, 'BeakUpper', [
      { transform:'rotate(0deg)' },
      { transform:'rotate(-12deg)' },
      { transform:'rotate(0deg)' }
    ], { duration: durJaw, easing: ease, fill:'none' }, 'caw')?.finished);
    anims.push(animateBone(lo.id, 'BeakLower', [
      { transform:'rotate(0deg)' },
      { transform:'rotate(34deg)' },
      { transform:'rotate(0deg)' }
    ], { duration: durJaw, easing: ease, fill:'none' }, 'caw')?.finished);

    return Promise.all(anims).then(()=>{});
  }

  function walk(){
    const crow = svg.getElementById('Crow');
    const head = svg.getElementById('Head');
    const skull = svg.getElementById('HeadSkull');
    const skullTop = svg.getElementById('SkullTop');
    const neckU = svg.getElementById('NeckUpper') || svg.getElementById('NeckMid');
    const hipL  = svg.getElementById('HipLeft')   || svg.getElementById('LegLeft');
    const anklL = svg.getElementById('AnkleLeft') || svg.getElementById('FootLeft');
    const toeL  = svg.getElementById('ToesLeft')  || svg.getElementById('FootLeft');
    const hipR  = svg.getElementById('HipRight')   || svg.getElementById('LegRight');
    const anklR = svg.getElementById('AnkleRight') || svg.getElementById('FootRight');
    const toeR  = svg.getElementById('ToesRight')  || svg.getElementById('FootRight');
    if (!crow || !head) return Promise.resolve();
    // Horizontal advance accumulator
    if (typeof walk.baseX !== 'number') walk.baseX = 0;
    const stepDist = 160; // greater forward motion so the walk is visible
    const x0 = walk.baseX;
    const x1 = x0 + stepDist;
    crow.style.transform = `translate(${x0}px, 0px)`;
    crow.animate(
      [
        { transform: `translate(${x0}px, 0px)` },
        { transform: `translate(${x1}px, 0px)` }
      ],
      { duration: 600, easing: 'steps(2,end)', fill: 'none' }
    ).finished.then(() => { walk.baseX = x1; crow.style.transform = `translate(${walk.baseX}px, 0px)`; }).catch(()=>{});
    head.animate(
      [
        { transform: 'translateY(0px)' },
        { transform: 'translateY(4px)' },
        { transform: 'translateY(0px)' }
      ],
      { duration: 300, iterations: 2, easing: 'ease-in-out', fill: 'none' }
    );
    if (neckU) animateBone(neckU.id || 'NeckUpper','NeckUpper',[
      { transform:'rotate(0deg)' }, { transform:'rotate(-2.5deg)' }, { transform:'rotate(0deg)' }
    ], { duration: 600, easing:'ease-in-out', fill:'none' }, 'walk');
    if (skull) animateBone(skull.id || 'HeadSkull','HeadSkull',[
      { transform:'rotate(0deg)' }, { transform:'rotate(-2deg)' }, { transform:'rotate(0deg)' }
    ], { duration: 600, easing:'ease-in-out', fill:'none' }, 'walk');
    if (skullTop) animateBone('SkullTop','SkullTop',[
      { transform:'rotate(0deg)' }, { transform:'rotate(-2.8deg)' }, { transform:'rotate(0deg)' }
    ], { duration: 600, easing:'ease-in-out', fill:'none' }, 'walk');
    const step = (hip, ankl, toe, delay) => {
      if (hip)  hip.animate(
        [ { transform:'rotate(0deg)' }, { transform:'rotate(8deg)' }, { transform:'rotate(0deg)' } ],
        { duration: 300, delay, easing:'ease-in-out', fill:'none' }
      );
      if (ankl) ankl.animate(
        [ { transform:'rotate(0deg)' }, { transform:'rotate(-6deg)' }, { transform:'rotate(0deg)' } ],
        { duration: 300, delay: delay+30, easing:'ease-in-out', fill:'none' }
      );
      if (toe)  toe.animate(
        [ { transform:'rotate(0deg)' }, { transform:'rotate(6deg)' }, { transform:'rotate(0deg)' } ],
        { duration: 300, delay: delay+50, easing:'ease-in-out', fill:'none' }
      );
    };
    step(hipL, anklL, toeL, 0);
    step(hipR, anklR, toeR, 300);
    dispatch('interact');
    return Promise.resolve();
  }

  /* -------------------------------------------------------------
     CSS loop helpers (class toggles on host)
  ------------------------------------------------------------- */
  const startLoop = (cls) => { if (host) host.classList.add(cls); };
  const stopLoop  = (cls) => { if (host) host.classList.remove(cls); };
  const headBobStart = () => startLoop('loop-headBob');
  const headBobStop  = () => stopLoop('loop-headBob');
  const preenStart   = () => startLoop('loop-preen');
  const preenStop    = () => stopLoop('loop-preen');
  const hopStart     = () => startLoop('loop-hop');
  const hopStop      = () => stopLoop('loop-hop');
  const walkStart    = () => startLoop('loop-walk');
  const walkStop     = () => stopLoop('loop-walk');

  async function cancel(){
    try { activeAnims.forEach(a => a.cancel()); } catch {}
    activeAnims.clear();
  }

  async function reset(){
    await cancel();
    if (host) {
      const toRemove = Array.from(host.classList).filter(c => c.startsWith('loop-') || c.startsWith('animate-'));
      toRemove.forEach(c => host.classList.remove(c));
    }
    // Enforce neutral transforms for critical bones and eyelids
    try {
      const hu = svg?.getElementById('HeadSkull') || svg?.getElementById('HeadUpper') || svg?.getElementById('Head');
      const st = svg?.getElementById('SkullTop');
      const bu = svg?.getElementById('BeakUpper');
      const bl = svg?.getElementById('BeakLower');
      const nu = svg?.getElementById('NeckUpper') || svg?.getElementById('NeckMid');
      const nb = svg?.getElementById('NeckBase');
      if (hu) hu.style.transform = 'rotate(0deg)';
      if (st) st.style.transform = 'rotate(0deg)';
      if (bu) bu.style.transform = 'rotate(0deg)';
      if (bl) bl.style.transform = 'rotate(0deg)';
      if (nu) nu.style.transform = 'translate(0px, 0px) rotate(0deg)';
      if (nb) nb.style.transform = 'rotate(0deg)';
      const up = svg?.getElementById('EyelidUpper');
      const lo = svg?.getElementById('EyelidLower');
      const upUnder = svg?.getElementById('EyelidUpperUnderlay');
      const loUnder = svg?.getElementById('EyelidLowerUnderlay');
      if (up) { up.style.opacity = '0'; up.style.transform = ''; }
      if (lo) { lo.style.opacity = '0'; lo.style.transform = ''; }
      if (upUnder) upUnder.style.opacity = '0';
      if (loUnder) loUnder.style.opacity = '0';
    } catch {}
  }

  /* -------------------------------------------------------------
     Mount: fetch, underpaint, mask dilation, beak guards, pivots
  ------------------------------------------------------------- */
  onMount(async () => {
    const ns = 'http://www.w3.org/2000/svg';
    const text = await fetch(src).then(r => r.text());
    host.innerHTML = text;
    svg = host.querySelector('svg') || host.firstElementChild;

    ensureIds();
    ensureHeadUpperGroup();
    ensureHeadGroups();
    ensureSkeleton();
    ensureAnimationStyle();
    if (devOverlayEnabled()) drawDevOverlay();
    // Presence flags for fallback CSS selectors (set on host wrapper)
    if (svg.getElementById('Head')) host.classList.add('has-head');
    if (svg.getElementById('Wing')) host.classList.add('has-wing');

    // Underpaint full silhouette once under all moving parts (hides any seams)
    const crowRoot = svg.getElementById('Crow');
    const crowPNG  = svg.getElementById('crowPNG');
    const silMask  = svg.getElementById('silMask');
    if (crowRoot && crowPNG && silMask && !svg.getElementById('Underpaint')) {
      const base = document.createElementNS(ns,'g');
      base.setAttribute('id','Underpaint');
      base.setAttribute('mask','url(#silMask)');
      const use = document.createElementNS(ns,'use'); use.setAttribute('href','#crowPNG');
      base.appendChild(use);
      crowRoot.parentNode.insertBefore(base, crowRoot);
    }
    // Hide the carving source if present
    const body = svg.getElementById('Body');
    if (body) body.setAttribute('display','none');

    // Dilation across masks; extra on beaks to fully preserve the tip
    ['maskLegL','maskLegR','maskFootL','maskFootR','maskTailA','maskTailB','maskTailC','maskTailD','maskWing','maskWingA','maskWingB','maskWingC','maskNeck','maskHead','maskHeadBase','maskSkullTop']
      .forEach(id => dilateMask(id, 1.0));
    ['maskBeakUpper','maskBeakLower'].forEach(id => dilateMask(id, 1.6));

    // Generous clip windows for beaks (viewBox-relative)
    const vb = svg.viewBox.baseVal || { x:0,y:0,width: svg.width.baseVal.value, height: svg.height.baseVal.value };
    clipBeak('BeakUpper', vb.width*0.56, vb.height*0.12, vb.width*0.98, vb.height*0.38);
    clipBeak('BeakLower', vb.width*0.56, vb.height*0.20, vb.width*0.98, vb.height*0.48);

    // Set anatomical pivots + perf hints
    prepareRig();
    await reset();

    // Ensure neutral beak/head state (closed beak, neutral skull)
    try {
      const hu = svg.getElementById('HeadSkull') || svg.getElementById('HeadUpper') || svg.getElementById('Head');
      const bu = svg.getElementById('BeakUpper');
      const bl = svg.getElementById('BeakLower');
      if (hu) hu.style.transform = 'rotate(0deg)';
      if (bu) bu.style.transform = 'rotate(0deg)';
      if (bl) bl.style.transform = 'rotate(0deg)';
    } catch {}

    // Ambient micro-behavior (respect reduceMotion)
    const onEnter = () => headBob();
    const onClick = () => { hop(); dispatch('interact'); };
    if (!reduceMotion) {
      host.addEventListener('mouseenter', onEnter);
      host.addEventListener('click', onClick);
    }

    // Expose API + host element for ambient scheduler
    dispatch('ready', { api: { blink, caw, headBob, preen, hop, walk, headBobStart, headBobStop, preenStart, preenStop, hopStart, hopStop, walkStart, walkStop, cancel, reset }, el: host });

    // Window-level caw => beak animation
    const onCawEvent = () => caw();
    window.addEventListener('corvid-caw', onCawEvent);
    // Dev overlay toggle via custom event
    const onOverlay = (e) => {
      const enabled = !!(e && e.detail && e.detail.enabled);
      if (enabled) drawDevOverlay();
      else {
        const ov = svg.getElementById('DevOverlay');
        if (ov && ov.parentNode) ov.parentNode.removeChild(ov);
        cancelOverlayTelemetry();
      }
      try { localStorage.setItem('corvidDevOverlay', enabled ? '1' : '0'); } catch {}
    };
    window.addEventListener('corvid-dev-overlay', onOverlay);

    onDestroy(() => {
      if (!reduceMotion) {
        host.removeEventListener('mouseenter', onEnter);
        host.removeEventListener('click', onClick);
      }
      window.removeEventListener('corvid-caw', onCawEvent);
      window.removeEventListener('corvid-dev-overlay', onOverlay);
    });
  });
</script>

<div class="crow" bind:this={host} aria-label="Crow rig"></div>

<style>
  .crow :global(.rig), .crow :global([id]){ transform-box: fill-box; }
  .crow :global(svg){ shape-rendering: geometricPrecision; }

</style>
