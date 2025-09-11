<script>
  import { onMount, onDestroy } from 'svelte'
  import { fly } from 'svelte/transition'
  import CrowRig from './lib/CrowRig.svelte'
  import SettingsPanel from './lib/SettingsPanel.svelte'
  import { decide } from './lib/brain.js'   // returns { actions:[...] }

  let audio
  let muted = false
  let volume = 0.8
  let reduceMotion = false

  // handle to the rig API CrowRig exposes via on:ready
  let rig
  const loops = { head:false, preen:false, hop:false }

  // ====== audio (yours, unchanged) ======
  async function synthCaw(vol = 0.8) {
    try {
      const Ctx = window.AudioContext || window.webkitAudioContext
      if (!Ctx || muted) return
      const ctx = new Ctx()
      const makeBurst = (offset = 0) => {
        const dur = 0.22, now = ctx.currentTime + offset
        const buffer = ctx.createBuffer(1, ctx.sampleRate * dur, ctx.sampleRate)
        const data = buffer.getChannelData(0)
        for (let i = 0; i < data.length; i++) data[i] = (Math.random() * 2 - 1)
        const noise = ctx.createBufferSource(); noise.buffer = buffer
        const bp = ctx.createBiquadFilter(); bp.type = 'bandpass'
        bp.frequency.setValueAtTime(780, now)
        bp.frequency.exponentialRampToValueAtTime(520, now + dur)
        bp.Q.value = 6
        const drive = ctx.createWaveShaper()
        const curve = new Float32Array(256)
        for (let i = 0; i < 256; i++) { const x = (i / 128) - 1; curve[i] = Math.tanh(2.5 * x) }
        drive.curve = curve
        const comp = ctx.createDynamicsCompressor(); comp.threshold.value = -18
        const g = ctx.createGain()
        g.gain.setValueAtTime(0.0001, now)
        g.gain.exponentialRampToValueAtTime(0.6 * vol, now + 0.015)
        g.gain.exponentialRampToValueAtTime(0.0001, now + dur)
        noise.connect(bp).connect(drive).connect(comp).connect(g).connect(ctx.destination)
        noise.start(now); noise.stop(now + dur)
      }
      makeBurst(0); makeBurst(0.12)
      setTimeout(() => ctx.close(), 600)
    } catch {}
  }

  // ====== unified actions ======
  async function caw() {
    try { await rig?.caw() } catch {}
    if (muted) return
    if (audio && audio.play) {
      try { audio.currentTime = 0; audio.volume = volume; audio.muted = false; await audio.play(); }
      catch {}
    } else {
      await synthCaw(volume)
    }
    try { window.dispatchEvent(new CustomEvent('corvid-caw')) } catch {}
  }
  const blink = () => rig?.blink()
  function toggleHead(){ loops.head = !loops.head; loops.head ? rig?.headBobStart() : rig?.headBobStop() }
  function togglePreen(){ loops.preen = !loops.preen; loops.preen ? rig?.preenStart() : rig?.preenStop() }
  function toggleHop(){ loops.hop = !loops.hop; loops.hop ? rig?.hopStart() : rig?.hopStop() }

  // CrowRig signals when its SVG is mounted
  function onCrowReady(e){ rig = e.detail.api }

  // LLM-driven reactions
  async function reactTo(eventName, payload = {}) {
    if (!rig) return
    const directive = await decide({ event: eventName, payload, reduceMotion })
    for (const a of directive.actions ?? []) {
      if (a.type === 'blink') await blink()
      if (a.type === 'caw')   await caw()
      if (a.type === 'hop' && !reduceMotion)   { if (!loops.hop)   toggleHop();   setTimeout(()=> loops.hop   && toggleHop(),   a.ms ?? 900) }
      if (a.type === 'preen' && !reduceMotion) { if (!loops.preen) togglePreen(); setTimeout(()=> loops.preen && togglePreen(), a.ms ?? 2400) }
      if (a.type === 'headBob' && !reduceMotion){ if (!loops.head) toggleHead();  setTimeout(()=> loops.head  && toggleHead(),  a.ms ?? 1200) }
    }
  }

  // ---- Global listeners to satisfy a11y (no handlers on <main>) ----
  function handleGlobalClick(){ reactTo('click') }
  function handleGlobalMove(){  reactTo('move') }
  function handleGlobalKey(e){
    const isEnter = e.key === 'Enter'
    const isSpace = e.key === ' ' || e.code === 'Space'
    if (isEnter || isSpace){
      // Don’t steal focus or scroll on Space
      e.preventDefault()
      reactTo('click', { source:'kbd' })
    }
  }

  onMount(() => {
    window.addEventListener('click', handleGlobalClick)
    window.addEventListener('mousemove', handleGlobalMove)
    window.addEventListener('keydown', handleGlobalKey)
    try { audio?.load?.() } catch {}

    return () => {
      window.removeEventListener('click', handleGlobalClick)
      window.removeEventListener('mousemove', handleGlobalMove)
      window.removeEventListener('keydown', handleGlobalKey)
    }
  })
</script>

<main class="page"
      role="region"
      aria-label="Corvid interactive region"
      in:fly={{ y: 24, duration: 700 }}>
  <div class="bg-iris" aria-hidden="true" />

  <header class="hero">
    <h1 class="sr-only">Corvid</h1>
    <button class="logo" on:click={caw} aria-label="Play crow caw">
      <img class="brand" src="/corvid_logo.png" alt="Corvid logo" loading="eager" />
    </button>
    <p class="tag">Iridescent social cognition in motion</p>
  </header>

  <!-- CrowRig should load the SVG inline and expose its API via on:ready -->
  <CrowRig reduceMotion={reduceMotion} on:ready={onCrowReady} on:interact={caw} />

  <section class="cta">
    <button class="caw" on:click={caw} aria-label="Caw">Caw</button>
    {#if false}
      <!-- optional dev controls -->
      <button on:click={blink}>Blink</button>
      <button on:click={toggleHead}>{loops.head ? 'Stop' : 'Start'} Head-bob</button>
      <button on:click={togglePreen}>{loops.preen ? 'Stop' : 'Start'} Preen</button>
      <button on:click={toggleHop}>{loops.hop ? 'Stop' : 'Start'} Hop</button>
    {/if}
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
      Corvid explores social cognition with a crow-inspired aesthetic—
      iridescent materials, measured motion, and playful micro-interactions.
      Built with Svelte + Vite and deployed on GitHub Pages.
    </p>
  </section>

  <footer class="site-foot">
    <a href="https://github.com/jfischburg-wci/cognitiveos-historical-social-model" target="_blank" rel="noopener">Repository</a>
    <span>•</span>
    <a href="https://github.com/users/jfischburg-wci/projects/4" target="_blank" rel="noopener">Project Board</a>
  </footer>

  <!-- Optional: place crow-caw.mp3 into frontend/public/ to enable -->
  <audio bind:this={audio} preload="auto">
    <source src="/crow-caw.mp3" type="audio/mpeg" />
    <source src="/crow-caw.wav" type="audio/wav" />
  </audio>

  <SettingsPanel bind:muted bind:volume bind:reduceMotion on:caw={caw} />
</main>

<style>
  :global(:root){
    --bg:#0d0f10; --ink:#e6eef7; --charcoal:#0f1113;
    --iris-1:#111827; --iris-2:#1e293b; --iris-3:#0ea5e9; --iris-4:#8b5cf6; --iris-5:#22d3ee; --accent:#82f7ff;
  }
  .page{
    position:relative; min-height:100vh; color:var(--ink);
    background: radial-gradient(1200px 800px at 70% 10%, #10202a 0%, transparent 60%), var(--charcoal);
    overflow-x:hidden;
  }
  .bg-iris{
    position:absolute; inset:-20% -10% auto -10%; height:70vh;
    background:conic-gradient(from 40deg at 30% 50%, rgba(34,211,238,.25), rgba(139,92,246,.2), rgba(14,165,233,.25), rgba(34,211,238,.25));
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