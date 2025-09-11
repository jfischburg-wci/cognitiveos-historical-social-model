Here’s a lint-clean, complete drop-in src/App.svelte that wires ambient behaviors (blink/head-bob/preen/hop + caw), respects reduceMotion, supports Enter/Space on the interactive region, and keeps your LLM reactions:

<script>
  import { onMount, onDestroy } from 'svelte';
  import { fly } from 'svelte/transition';
  import CrowRig from './lib/CrowRig.svelte';
  import SettingsPanel from './lib/SettingsPanel.svelte';
  import { startAmbient } from './lib/ambient.js';
  import { decide } from './lib/brain.js';

  let audio;
  let muted = false;
  let volume = 0.8;
  let reduceMotion = false;

  let rig;               // API from CrowRig (blink, caw, headBob, preen, hop)
  let crowEl;            // DOM element CrowRig renders into (for hop drift)
  let ambientHandle;     // controller returned by startAmbient()

  // --- caw with file-first playback and synth fallback ---
  async function caw() {
    try { await rig?.caw(); } catch {}
    if (muted) return;

    if (audio?.play) {
      try {
        audio.currentTime = 0;
        audio.volume = volume;
        audio.muted = false;
        await audio.play();
      } catch {
        await synthCaw(volume);
      }
    } else {
      await synthCaw(volume);
    }

    try { window.dispatchEvent(new CustomEvent('corvid-caw')); } catch {}
  }

  // Lightweight synthetic crow (fallback only)
  async function synthCaw(vol = 0.8) {
    try {
      const Ctx = window.AudioContext || window.webkitAudioContext;
      if (!Ctx || muted) return;
      const ctx = new Ctx();
      const burst = (offset = 0) => {
        const dur = 0.18, now = ctx.currentTime + offset;
        const buffer = ctx.createBuffer(1, ctx.sampleRate * dur, ctx.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < data.length; i++) data[i] = (Math.random() * 2 - 1);

        const noise = ctx.createBufferSource(); noise.buffer = buffer;
        const bp = ctx.createBiquadFilter(); bp.type = 'bandpass';
        bp.frequency.setValueAtTime(720, now);
        bp.frequency.exponentialRampToValueAtTime(560, now + dur);
        bp.Q.value = 5.2;

        const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 4200;

        const drive = ctx.createWaveShaper();
        const curve = new Float32Array(256);
        for (let i = 0; i < 256; i++) { const x = i / 128 - 1; curve[i] = Math.tanh(1.9 * x); }
        drive.curve = curve;

        const comp = ctx.createDynamicsCompressor();
        comp.threshold.value = -20; comp.knee.value = 12; comp.ratio.value = 6;

        const gain = ctx.createGain();
        gain.gain.setValueAtTime(0.0001, now);
        gain.gain.exponentialRampToValueAtTime(0.55 * vol, now + 0.014);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + dur);

        noise.connect(bp).connect(lp).connect(drive).connect(comp).connect(gain).connect(ctx.destination);
        noise.start(now); noise.stop(now + dur);
      };
      burst(0); burst(0.11);
      setTimeout(() => ctx.close(), 500);
    } catch {}
  }

  // CrowRig ready → keep API/element and start ambient (unless reduced motion)
  function onCrowReady(e) {
    rig    = e.detail.api;
    crowEl = e.detail.el;
    ambientHandle?.stop?.();
    ambientHandle = startAmbient({ rig, el: crowEl, caw, reduceMotion });
  }

  // Recreate ambient loop if reduceMotion toggles at runtime
  $: if (rig && crowEl) {
    ambientHandle?.stop?.();
    ambientHandle = startAmbient({ rig, el: crowEl, caw, reduceMotion });
  }

  onDestroy(() => ambientHandle?.stop?.());

  // LLM-driven reactions
  async function reactTo(eventName, payload = {}) {
    if (!rig) return;
    const directive = await decide({ event: eventName, payload, reduceMotion });
    for (const action of directive.actions || []) {
      if (action.type === 'blink') await rig.blink();
      if (action.type === 'caw')   await caw();
      if (action.type === 'hop'    && !reduceMotion) await rig.hop();
      if (action.type === 'preen'  && !reduceMotion) await rig.preen();
      if (action.type === 'headBob'&& !reduceMotion) await rig.headBob();
    }
  }

  // A11y: Enter/Space act like click on the interactive surface
  function handleKey(e) {
    const isEnter = e.key === 'Enter';
    const isSpace = e.key === ' ' || e.code === 'Space';
    if (isEnter || isSpace) { e.preventDefault(); reactTo('click', { source: 'kbd' }); }
  }

  onMount(() => { try { audio?.load?.() } catch {} });
</script>

<main class="page" in:fly={{ y: 24, duration: 700 }}>
  <div class="bg-iris" aria-hidden="true"></div>

  <!-- Interactive region: keyboard & pointer handlers live here (not on <main>) -->
  <div
    class="surface"
    role="button"
    tabindex="0"
    aria-label="Corvid interactive region"
    on:click={() => reactTo('click')}
    on:mousemove={() => reactTo('move')}
    on:keydown={handleKey}
  >
    <header class="hero">
      <h1 class="sr-only">Corvid</h1>
      <button class="logo" on:click={caw} aria-label="Play crow caw">
        <img class="brand" src="/corvid_logo.png" alt="Corvid logo" loading="eager" />
      </button>
      <p class="tag">Iridescent social cognition in motion</p>
    </header>

    <CrowRig reduceMotion={reduceMotion} on:ready={onCrowReady} on:interact={caw} />

    <section class="cta">
      <button class="caw" on:click={caw} aria-label="Caw">Caw</button>
    </section>

    <section class="coming">
      <h2>Coming Soon</h2>
      <p>
        We’re crafting an iridescent, crow-inspired exploration of social cognition.
        Scroll-driven parallax, subtle micro-interactions, and a bold technical
        typographic system are landing shortly.
      </p>
    </section>

    <section class="features">
      <div class="feature"><h3>Iridescent Theme</h3><p>Charcoal base with spectral highlights and soft bloom.</p></div>
      <div class="feature"><h3>Motion Craft</h3><p>Motion One animations for parallax, entrances, and micro-states.</p></div>
      <div class="feature"><h3>Crow Interactions</h3><p>Hops, blinks, and context cues—tasteful, responsive, and accessible.</p></div>
    </section>

    <section class="about">
      <h2>About Corvid</h2>
      <p>
        Corvid explores social cognition with a crow-inspired aesthetic—iridescent
        materials, measured motion, and playful micro-interactions. Built with
        Svelte + Vite and deployed on GitHub Pages.
      </p>
    </section>

    <footer class="site-foot">
      <a href="https://github.com/jfischburg-wci/cognitiveos-historical-social-model" target="_blank" rel="noopener">Repository</a>
      <span>•</span>
      <a href="https://github.com/users/jfischburg-wci/projects/4" target="_blank" rel="noopener">Project Board</a>
    </footer>

    <audio bind:this={audio} preload="auto">
      <source src="/crow-caw.wav" type="audio/wav" />
      <source src="/crow-caw.mp3" type="audio/mpeg" />
    </audio>

    <SettingsPanel bind:muted bind:volume bind:reduceMotion on:caw={caw} />
  </div>
</main>

<style>
  :global(:root){
    --bg:#0d0f10; --ink:#e6eef7; --charcoal:#0f1113;
    --iris-1:#111827; --iris-2:#1e293b; --iris-3:#0ea5e9; --iris-4:#8b5cf6; --iris-5:#22d3ee; --accent:#82f7ff;
  }
  .page{
    position:relative;
    min-height:100vh;
    color:var(--ink);
    background: radial-gradient(1200px 800px at 70% 10%, #10202a 0%, transparent 60%), var(--charcoal);
    overflow-x:hidden;
  }
  .surface{ outline:none }
  .surface:focus-visible{ outline:2px solid #82f7ff; outline-offset:4px }

  .bg-iris{
    position:absolute; inset:-20% -10% auto -10%; height:70vh;
    background:conic-gradient(from 40deg at 30% 50%,
      rgba(34,211,238,.25), rgba(139,92,246,.2), rgba(14,165,233,.25), rgba(34,211,238,.25));
    filter:blur(48px) saturate(130%); opacity:.6; pointer-events:none;
  }
  .hero{ padding:7rem 2rem 2rem; text-align:center; }
  .sr-only{ position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0 }
  .logo{ background:none; border:0; display:inline-block; cursor:pointer; padding:0 }
  .brand{ width:min(80vw, 720px); height:auto; filter:drop-shadow(0 10px 40px rgba(130,247,255,.2)); }
  .tag{ opacity:.8; margin:.5rem 0 0; letter-spacing:.08em; }
  .cta{ display:flex; justify-content:center; gap:.6rem; padding:3rem 0 6rem; }
  .caw{
    appearance:none; border:1px solid rgba(130,247,255,.35); color:var(--ink);
    background:linear-gradient(180deg, rgba(130,247,255,.07), rgba(255,255,255,.02));
    padding:.8rem 1.2rem; border-radius:999px; letter-spacing:.06em; backdrop-filter: blur(6px);
    box-shadow: inset 0 0 0 1px rgba(255,255,255,.04), 0 6px 30px rgba(0,0,0,.4);
  }
  .coming{ max-width:820px; margin:0 auto; padding:1rem 2rem 2rem; text-align:center; }
  .coming h2{ font-size: clamp(28px, 6vw, 48px); margin:0 0 .3rem; letter-spacing:.06em; }
  .features{ display:grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap:1rem; max-width:1100px; margin:1.5rem auto 5rem; padding:0 1rem; }
  .feature{ padding:1rem; border-radius:16px; border:1px solid rgba(130,247,255,.2); background:linear-gradient(180deg, rgba(130,247,255,.05), rgba(255,255,255,.02)); }
  .feature h3{ margin:.2rem 0 .4rem; letter-spacing:.04em; }
  @media (max-width: 900px){ .features{ grid-template-columns: 1fr } }
  .about{ max-width:820px; margin:0 auto 3rem; padding:0 2rem; text-align:center; opacity:.9 }
  .site-foot{ display:flex; gap:.6rem; justify-content:center; padding:2rem; opacity:.7 }
  .site-foot a{ color:#82f7ff; text-decoration:none }
</style>