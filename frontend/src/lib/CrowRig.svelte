<script>
  import { createEventDispatcher, onMount, onDestroy } from 'svelte';

  // Props
  export let src = '/corvid_crow_anim_v9.svg';
  export let reduceMotion = false; // respected below

  // State
  const dispatch = createEventDispatcher();
  let host, svg;
  const activeAnims = new Set();

  function track(anim){
    if (!anim) return anim;
    try {
      activeAnims.add(anim);
      anim.onfinish = () => activeAnims.delete(anim);
      anim.oncancel = () => activeAnims.delete(anim);
    } catch {}
    return anim;
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
    const BU   = { x: vb.width*0.60, y: vb.height*0.23 };
    const BL   = { x: vb.width*0.61, y: vb.height*0.26 };
    const TAIL = { x: vb.width*0.19, y: vb.height*0.62 };
    const LFOOT= { x: vb.width*0.37, y: vb.height*0.82 };
    const RFOOT= { x: vb.width*0.49, y: vb.height*0.82 };

    setOrigin('Head', HEAD.x, HEAD.y);
    setOrigin('Wing',  WING.x,  WING.y);
    setOrigin('WingA', WINGA.x, WINGA.y);
    setOrigin('WingB', WINGB.x, WINGB.y);
    setOrigin('WingC', WINGC.x, WINGC.y);
    setOrigin('BeakUpper', BU.x, BU.y);
    setOrigin('BeakLower', BL.x, BL.y);
    ['TailA','TailB','TailC','TailD'].forEach(id => setOrigin(id, TAIL.x, TAIL.y));
    setOrigin('FootLeft',  LFOOT.x, LFOOT.y);
    setOrigin('FootRight', RFOOT.x, RFOOT.y);

    // Hint to engines that these nodes will animate transforms
    ['Crow','Head','Wing','WingA','WingB','WingC','BeakUpper','BeakLower','TailA','TailB','TailC','TailD','Legs','Feet','FootLeft','FootRight']
      .forEach(id => { const el = svg.getElementById(id); if (el) el.style.willChange = 'transform'; });
  }

  /* -------------------------------------------------------------
     WAAPI animation functions (anatomical)
  ------------------------------------------------------------- */

  function blink(){
    const up = svg.getElementById('EyelidUpper');
    const lo = svg.getElementById('EyelidLower');
    if (!up || !lo) return Promise.resolve();

    // Ensure eyelids only: set transform origins and make visible during blink
    up.style.transformBox = 'fill-box';
    lo.style.transformBox = 'fill-box';
    up.style.transformOrigin = '50% 100%'; // center-bottom
    lo.style.transformOrigin = '50% 0%';   // center-top
    up.style.opacity = '1';
    lo.style.opacity = '1';

    const kf = [
      { transform: 'scaleY(0)' },
      { transform: 'scaleY(1)' },
      { transform: 'scaleY(0)' }
    ];

    const quick = 140;
    const slow  = 220;

    const aU1 = track(up.animate(kf, { duration: quick, easing: 'ease-in-out', fill: 'none' }));
    const aL1 = track(lo.animate(kf, { duration: quick, easing: 'ease-in-out', fill: 'none' }));

    const maybeSecond = Math.random() < 0.35;

    return Promise.all([aU1.finished, aL1.finished]).then(async () => {
      if (maybeSecond) {
        await new Promise(r => setTimeout(r, 60));
        const aU2 = track(up.animate(kf, { duration: slow, easing: 'ease-in-out', fill: 'none' }));
        const aL2 = track(lo.animate(kf, { duration: slow, easing: 'ease-in-out', fill: 'none' }));
        await Promise.all([aU2.finished, aL2.finished]);
      }
      // Hide eyelids again (neutral)
      up.style.opacity = '0';
      lo.style.opacity = '0';
    });
  }

  function headBob(){
    const head = svg.getElementById('Head');
    if (!head) return Promise.resolve();
    return head.animate(
      [{ transform:'translateY(0) rotate(0deg)' },
       { transform:'translateY(6px) rotate(-2deg)' },
       { transform:'translateY(0) rotate(0deg)' }],
      { duration: 900, easing:'cubic-bezier(.3,.6,.3,1)', fill:'none' }
    ).finished;
  }

  function preen(){
    const wing = svg.getElementById('Wing');
    const wingC = svg.getElementById('WingC');
    const tails = ['TailA','TailB','TailC','TailD'].map(id=>svg.getElementById(id)).filter(Boolean);
    if (!wing) return Promise.resolve();
    wing.animate(
      [{ transform:'rotate(0deg)' },
       { transform:'rotate(-6deg)' },
       { transform:'rotate(3deg)'  },
       { transform:'rotate(0deg)' }],
      { duration: 1600, easing:'ease-in-out', fill:'none' }
    );
    // Subtle delayed tip follow-through
    if (wingC) {
      wingC.animate(
        [{ transform:'rotate(0deg)' }, { transform:'rotate(-2deg)' }, { transform:'rotate(1deg)' }, { transform:'rotate(0deg)' }],
        { duration: 1600, delay: 120, easing:'ease-in-out', fill:'none' }
      );
    }
    tails.forEach((t,i)=>{
      t.animate(
        [{ transform:'rotate(0deg)' }, { transform:`rotate(${i%2?2:-2}deg)` }, { transform:'rotate(0deg)' }],
        { duration: 1200, delay: i*60, easing:'ease-in-out', fill:'none' }
      );
    });
    return Promise.resolve();
  }

  function hop(){
    const crow = svg.getElementById('Crow');
    const feet = [svg.getElementById('FootLeft'), svg.getElementById('FootRight')].filter(Boolean);
    if (!crow) return Promise.resolve();
    crow.animate(
      [{ transform:'translateY(0)' }, { transform:'translateY(-20px)' }, { transform:'translateY(-8px)' }, { transform:'translateY(0)' }],
      { duration: 900, easing:'cubic-bezier(.3,.6,.3,1)', fill:'none' }
    );
    feet.forEach(f => f.animate(
      [{ transform:'rotate(0deg)' }, { transform:'rotate(8deg)' }, { transform:'rotate(0deg)' }],
      { duration: 400, easing:'ease-out', fill:'none' }
    ));
    dispatch('interact');
    return Promise.resolve();
  }

  function caw(){
    const up = svg.getElementById('BeakUpper');
    const lo = svg.getElementById('BeakLower');
    if (!up || !lo) return Promise.resolve();
    up.animate(
      [{ transform:'rotate(0)' }, { transform:'rotate(-12deg)' }, { transform:'rotate(0)' }],
      { duration: 600, easing:'ease-in-out', fill:'none' }
    );
    return lo.animate(
      [{ transform:'rotate(0)' }, { transform:'rotate(14deg)' }, { transform:'rotate(0)' }],
      { duration: 600, easing:'ease-in-out', fill:'none' }
    ).finished;
  }

  function walk(){
    const crow = svg.getElementById('Crow');
    const head = svg.getElementById('Head');
    if (!crow || !head) return Promise.resolve();
    crow.animate(
      [
        { transform: 'translateX(0px)' },
        { transform: 'translateX(32px)' }
      ],
      { duration: 600, easing: 'steps(2,end)', fill: 'none' }
    );
    head.animate(
      [
        { transform: 'translateY(0px)' },
        { transform: 'translateY(4px)' },
        { transform: 'translateY(0px)' }
      ],
      { duration: 300, iterations: 2, easing: 'ease-in-out', fill: 'none' }
    );
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
    ensureAnimationStyle();
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
    ['maskLegL','maskLegR','maskFootL','maskFootR','maskTailA','maskTailB','maskTailC','maskTailD','maskWing','maskWingA','maskWingB','maskWingC','maskNeck','maskHead']
      .forEach(id => dilateMask(id, 1.0));
    ['maskBeakUpper','maskBeakLower'].forEach(id => dilateMask(id, 1.6));

    // Generous clip windows for beaks (viewBox-relative)
    const vb = svg.viewBox.baseVal || { x:0,y:0,width: svg.width.baseVal.value, height: svg.height.baseVal.value };
    clipBeak('BeakUpper', vb.width*0.56, vb.height*0.12, vb.width*0.98, vb.height*0.38);
    clipBeak('BeakLower', vb.width*0.56, vb.height*0.20, vb.width*0.98, vb.height*0.48);

    // Set anatomical pivots + perf hints
    prepareRig();

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

    onDestroy(() => {
      if (!reduceMotion) {
        host.removeEventListener('mouseenter', onEnter);
        host.removeEventListener('click', onClick);
      }
      window.removeEventListener('corvid-caw', onCawEvent);
    });
  });
</script>

<div class="crow" bind:this={host} aria-label="Crow rig"></div>

<style>
  .crow :global(.rig), .crow :global([id]){ transform-box: fill-box; }
  .crow :global(svg){ shape-rendering: geometricPrecision; }
</style>
