<script>
  import { createEventDispatcher, onMount, onDestroy } from 'svelte';

  // Props
  export let src = '/corvid_crow_anim_v9.svg';
  export let reduceMotion = false; // respected below

  // State
  const dispatch = createEventDispatcher();
  let host, svg;

  // ------- one-shots (toggle classes the SVG understands) -------
  const once = (cls, ms) =>
    new Promise((res) => {
      if (!svg) return res();
      svg.classList.add(cls);
      setTimeout(() => { svg.classList.remove(cls); res(); }, ms);
    });

  const blink   = () => once('animate-blink',   240);
  const caw     = () => once('animate-caw',     600);
  const headBob = () => once('animate-headBob', 1200);
  const preen   = () => once('animate-preen',   2400);
  const hop     = () => { dispatch('interact'); return once('animate-hop', 900); };

  // ------- convenience: eyelid group if exported as two layers -------
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

  // ------- inject fallback animation CSS if asset didn’t ship with it -------
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
      .animate-headBob #Head{animation:headBob 1.2s ease-in-out 1}
      .animate-blink #EyelidUpper,.animate-blink #EyelidLower{transform-origin:50% 50%;animation:blink .24s 1}
      .animate-preen #Wing{transform-origin:33% 36%;animation:preen 2.4s ease-in-out 1}
      .animate-hop #Crow{animation:hop .9s cubic-bezier(.3,.6,.3,1) 1}
      .animate-caw #BeakUpper{transform-origin:60% 23%;animation:beakOpen .6s 1}
      .animate-caw #BeakLower{transform-origin:61% 26%;animation:beakLower .6s 1}
    `;
    const style = document.createElementNS('http://www.w3.org/2000/svg','style');
    style.textContent = css;
    svg.insertBefore(style, svg.firstChild);
  }

  // ------- per-mask dilation so parts overlap (no AA slits) -------
  function dilateMask(maskId, radiusPx) {
    const ns = 'http://www.w3.org/2000/svg';
    const m = svg.getElementById(maskId);
    if (!m) return;

    // ensure <defs>
    let defs = svg.querySelector('defs');
    if (!defs) { defs = document.createElementNS(ns,'defs'); svg.insertBefore(defs, svg.firstChild); }

    // build filter if missing
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

    // wrap mask children so the filter applies
    const wrap = document.createElementNS(ns,'g');
    wrap.setAttribute('filter', `url(#${fid})`);
    while (m.firstChild) wrap.appendChild(m.firstChild);
    m.appendChild(wrap);
  }

  // ------- generous hard clip for beaks so the tip never clips -------
  function clipBeak(id, x0,y0,x1,y1){
    const ns='http://www.w3.org/2000/svg';
    const g = svg.getElementById(id); if(!g) return;
    let defs = svg.querySelector('defs'); if(!defs){ defs=document.createElementNS(ns,'defs'); svg.insertBefore(defs, svg.firstChild); }
    const cpid=`cp-${id}`;
    if(!svg.getElementById(cpid)){
      const cp=document.createElementNS(ns,'clipPath'); cp.setAttribute('id',cpid);
      const r=document.createElementNS(ns,'rect');
      r.setAttribute('x',x0); r.setAttribute('y',y0);
      r.setAttribute('width',x1-x0); r.setAttribute('height',y1-y0);
      cp.appendChild(r); defs.appendChild(cp);
    }
    g.setAttribute('clip-path', `url(#${cpid})`);
  }

  onMount(async () => {
    const text = await fetch(src).then(r => r.text());
    host.innerHTML = text;
    svg = host.querySelector('svg') || host.firstElementChild;

    // Ensure rig IDs and fallback keyframes exist
    ensureIds();
    ensureAnimationStyle();

    // 1) Underpaint: paint full silhouette once under moving parts (hides any slits)
    const ns = 'http://www.w3.org/2000/svg';
    const crowRoot = svg.getElementById('Crow');
    const crowPNG  = svg.getElementById('crowPNG');
    const silMask  = svg.getElementById('silMask');
    if (crowRoot && crowPNG && silMask && !svg.getElementById('Underpaint')) {
      const base = document.createElementNS(ns,'g');
      base.setAttribute('id','Underpaint');
      base.setAttribute('mask','url(#silMask)');
      const use = document.createElementNS(ns,'use');
      use.setAttribute('href','#crowPNG');
      base.appendChild(use);
      crowRoot.parentNode.insertBefore(base, crowRoot);
    }
    // Optional: hide the carving source if present
    const body = svg.getElementById('Body');
    if (body) body.setAttribute('display','none');

    // 2) Dilation across masks; extra on beaks to restore lower tip
    ['maskLegL','maskLegR','maskFootL','maskFootR','maskTailA','maskTailB','maskTailC','maskTailD','maskWing','maskNeck','maskHead']
      .forEach(id => dilateMask(id, 1.0));
    ['maskBeakU','maskBeakL'].forEach(id => dilateMask(id, 1.6));

    // 3) Hard clip windows for beaks (protect the very tip)
    const vb = svg.viewBox.baseVal || { x:0,y:0,width: svg.width.baseVal.value, height: svg.height.baseVal.value };
    const bx0 = vb.width*0.56, by0 = vb.height*0.12, bx1 = vb.width*0.98, by1 = vb.height*0.38;  // upper
    const lx0 = vb.width*0.56, ly0 = vb.height*0.20, lx1 = vb.width*0.98, ly1 = vb.height*0.48;  // lower
    clipBeak('BeakUpper', bx0, by0, bx1, by1);
    clipBeak('BeakLower', lx0, ly0, lx1, ly1);

    // 4) Ambient micro-behavior (respect reduceMotion)
    let idle;
    const onEnter = () => headBob();
    const onClick = () => { hop(); dispatch('interact'); };
    if (!reduceMotion) {
      idle = setInterval(() => blink(), 3500 + Math.random()*2500);
      host.addEventListener('mouseenter', onEnter);
      host.addEventListener('click', onClick);
    }

    // Expose API + host el for ambient scheduler
    dispatch('ready', { api: { blink, caw, headBob, preen, hop }, el: host });

    // Global caw event → beak animation
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