<script>
  import { createEventDispatcher, onMount, onDestroy } from 'svelte';
  export let src = '/corvid_crow_anim_v9.svg';
  export let reduceMotion = false; // now respected

  const dispatch = createEventDispatcher();
  let host, svg;

  // ------- one-shot helpers (toggle classes the SVG understands) -------
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

  // ------- per-mask dilation so parts overlap (no AA seams) -------
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
      f.setAttribute('x','-10%'); f.setAttribute('y','-10%');
      f.setAttribute('width','120%'); f.setAttribute('height','120%');

      const morph = document.createElementNS(ns,'feMorphology');
      morph.setAttribute('operator','dilate');
      morph.setAttribute('radius', String(radiusPx));

      const blur = document.createElementNS(ns,'feGaussianBlur');
      blur.setAttribute('stdDeviation','0.15');

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

  onMount(async () => {
    const text = await fetch(src).then(r => r.text());
    host.innerHTML = text;
    svg = host.querySelector('svg') || host.firstElementChild;

    ensureIds();
    ensureAnimationStyle();

    // --- Overlap masks to remove gaps; pad beak so tip never clips ---
    ['maskBody','maskLegL','maskLegR','maskFootL','maskFootR','maskTailA','maskTailB','maskTailC','maskTailD']
      .forEach(id => dilateMask(id, 1.0));
    ['maskWing','maskNeck','maskHead'].forEach(id => dilateMask(id, 0.9));
    ['maskBeakU','maskBeakL'].forEach(id => dilateMask(id, 0.7));

    // --- Ambient/UX triggers (respect reduceMotion) ---
    let idle;
    const onEnter = () => headBob();
    const onClick = () => { hop(); dispatch('interact'); };

    if (!reduceMotion) {
      idle = setInterval(() => blink(), 3500 + Math.random()*2500);
      host.addEventListener('mouseenter', onEnter);
      host.addEventListener('click', onClick);
    }

    // Expose API upward
    dispatch('ready', { api: { blink, caw, headBob, preen, hop }});

    // sync with global caw events from App
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