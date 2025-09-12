<script>
  import { createEventDispatcher, onMount, onDestroy } from 'svelte';

  // Props
  export let src = '/corvid_crow_anim_v9.svg';
  export let reduceMotion = false; // respected below

  // State
  const dispatch = createEventDispatcher();
  let host, svg;

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
    const BU   = { x: vb.width*0.60, y: vb.height*0.23 };
    const BL   = { x: vb.width*0.61, y: vb.height*0.26 };
    const TAIL = { x: vb.width*0.19, y: vb.height*0.62 };
    const LFOOT= { x: vb.width*0.37, y: vb.height*0.82 };
    const RFOOT= { x: vb.width*0.49, y: vb.height*0.82 };

    setOrigin('Head', HEAD.x, HEAD.y);
    setOrigin('Wing', WING.x, WING.y);
    setOrigin('BeakUpper', BU.x, BU.y);
    setOrigin('BeakLower', BL.x, BL.y);
    ['TailA','TailB','TailC','TailD'].forEach(id => setOrigin(id, TAIL.x, TAIL.y));
    setOrigin('FootLeft',  LFOOT.x, LFOOT.y);
    setOrigin('FootRight', RFOOT.x, RFOOT.y);

    // Hint to engines that these nodes will animate transforms
    ['Crow','Head','Wing','BeakUpper','BeakLower','TailA','TailB','TailC','TailD','Legs','Feet','FootLeft','FootRight']
      .forEach(id => { const el = svg.getElementById(id); if (el) el.style.willChange = 'transform'; });
  }

  /* -------------------------------------------------------------
     WAAPI animation functions (anatomical)
  ------------------------------------------------------------- */

  function blink(){
    const up = svg.getElementById('EyelidUpper');
    const lo = svg.getElementById('EyelidLower');
    if (!up || !lo) return Promise.resolve();
    const opts = { duration: 140, easing: 'linear', fill: 'both' };
    up.animate([{ transform:'scaleY(1)' }, { transform:'scaleY(0.1)' }, { transform:'scaleY(1)' }], opts);
    return lo.animate([{ transform:'scaleY(1)' }, { transform:'scaleY(0.1)' }, { transform:'scaleY(1)' }], opts).finished;
  }

  function headBob(){
    const head = svg.getElementById('Head');
    if (!head) return Promise.resolve();
    return head.animate(
      [{ transform:'translateY(0) rotate(0deg)' },
       { transform:'translateY(6px) rotate(-2deg)' },
       { transform:'translateY(0) rotate(0deg)' }],
      { duration: 900, easing:'cubic-bezier(.3,.6,.3,1)', fill:'both' }
    ).finished;
  }

  function preen(){
    const wing = svg.getElementById('Wing');
    const tails = ['TailA','TailB','TailC','TailD'].map(id=>svg.getElementById(id)).filter(Boolean);
    if (!wing) return Promise.resolve();
    wing.animate(
      [{ transform:'rotate(0deg)' },
       { transform:'rotate(-6deg)' },
       { transform:'rotate(3deg)'  },
       { transform:'rotate(0deg)' }],
      { duration: 1600, easing:'ease-in-out', fill:'both' }
    );
    tails.forEach((t,i)=>{
      t.animate(
        [{ transform:'rotate(0deg)' }, { transform:`rotate(${i%2?2:-2}deg)` }, { transform:'rotate(0deg)' }],
        { duration: 1200, delay: i*60, easing:'ease-in-out', fill:'both' }
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
      { duration: 900, easing:'cubic-bezier(.3,.6,.3,1)', fill:'both' }
    );
    feet.forEach(f => f.animate(
      [{ transform:'rotate(0deg)' }, { transform:'rotate(8deg)' }, { transform:'rotate(0deg)' }],
      { duration: 400, easing:'ease-out', fill:'both' }
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
      { duration: 600, easing:'ease-in-out', fill:'both' }
    );
    return lo.animate(
      [{ transform:'rotate(0)' }, { transform:'rotate(14deg)' }, { transform:'rotate(0)' }],
      { duration: 600, easing:'ease-in-out', fill:'both' }
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
      { duration: 600, easing: 'steps(2,end)', fill: 'both' }
    );
    head.animate(
      [
        { transform: 'translateY(0px)' },
        { transform: 'translateY(4px)' },
        { transform: 'translateY(0px)' }
      ],
      { duration: 300, iterations: 2, easing: 'ease-in-out' }
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
    ['maskLegL','maskLegR','maskFootL','maskFootR','maskTailA','maskTailB','maskTailC','maskTailD','maskWing','maskNeck','maskHead']
      .forEach(id => dilateMask(id, 1.0));
    ['maskBeakU','maskBeakL'].forEach(id => dilateMask(id, 1.6));

    // Generous clip windows for beaks (viewBox-relative)
    const vb = svg.viewBox.baseVal || { x:0,y:0,width: svg.width.baseVal.value, height: svg.height.baseVal.value };
    clipBeak('BeakUpper', vb.width*0.56, vb.height*0.12, vb.width*0.98, vb.height*0.38);
    clipBeak('BeakLower', vb.width*0.56, vb.height*0.20, vb.width*0.98, vb.height*0.48);

    // Set anatomical pivots + perf hints
    prepareRig();

    // Ambient micro-behavior (respect reduceMotion)
    let idle;
    const onEnter = () => headBob();
    const onClick = () => { hop(); dispatch('interact'); };
    if (!reduceMotion) {
      idle = setInterval(() => blink(), 3500 + Math.random()*2500);
      host.addEventListener('mouseenter', onEnter);
      host.addEventListener('click', onClick);
    }

    // Expose API + host element for ambient scheduler
    dispatch('ready', { api: { blink, caw, headBob, preen, hop, walk, headBobStart, headBobStop, preenStart, preenStop, hopStart, hopStop, walkStart, walkStop }, el: host });

    // Window-level caw => beak animation
    const onCawEvent = () => caw();
    window.addEventListener('corvid-caw', onCawEvent);

    onDestroy(() => {
      if (idle) clearInterval(idle);
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
</style>
