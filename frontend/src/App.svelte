<script>
  import { onMount } from 'svelte'
  import { fly } from 'svelte/transition'
  import ParallaxCrow from './lib/ParallaxCrow.svelte'
  let audio
  function caw() {
    if (audio && audio.play) {
      audio.currentTime = 0
      audio.play().catch(() => {})
    }
  }
  onMount(() => {
    if (audio && audio.load) {
      try { audio.load() } catch {}
    }
  })
</script>

<div class="page" in:fly={{ y: 24, duration: 700 }}>
  <div class="bg-iris" aria-hidden="true" />

  <header class="hero">
    <h1 class="logo" on:click={caw}>CORVID</h1>
    <p class="tag">Iridescent social cognition in motion</p>
  </header>

  <ParallaxCrow />

  <section class="cta">
    <button class="caw" on:click={caw} aria-label="Caw">
      Caw
    </button>
  </section>

  <section class="coming">
    <h2>Coming Soon</h2>
    <p>
      We’re crafting an iridescent, crow-inspired exploration of social cognition.
      Scroll-driven parallax, subtle micro‑interactions, and a bold technical
      typographic system are landing shortly.
    </p>
  </section>

  <section class="features">
    <div class="feature">
      <h3>Iridescent Theme</h3>
      <p>Charcoal base with spectral highlights and soft bloom.</p>
    </div>
    <div class="feature">
      <h3>Motion Craft</h3>
      <p>Motion One animations for parallax, entrances, and micro‑states.</p>
    </div>
    <div class="feature">
      <h3>Crow Interactions</h3>
      <p>Hops, blinks, and context cues—tasteful, responsive, and accessible.</p>
    </div>
  </section>

  <!-- Optional: place crow-caw.mp3 into frontend/public/ to enable -->
  <audio bind:this={audio} src="/crow-caw.mp3" preload="auto" />
</div>

<style>
  :global(:root){
    --bg: #0d0f10;
    --ink: #e6eef7;
    --charcoal: #0f1113;
    --iris-1: #111827;
    --iris-2: #1e293b;
    --iris-3: #0ea5e9;
    --iris-4: #8b5cf6;
    --iris-5: #22d3ee;
    --accent: #82f7ff;
  }
  .page{
    position: relative;
    min-height: 100vh;
    color: var(--ink);
    background: radial-gradient(1200px 800px at 70% 10%, #10202a 0%, transparent 60%) , var(--charcoal);
    overflow-x: hidden;
  }
  .bg-iris{
    position: absolute; inset: -20% -10% auto -10%; height: 70vh;
    background: conic-gradient(from 40deg at 30% 50%,
      rgba(34, 211, 238, 0.25), rgba(139, 92, 246, 0.2), rgba(14, 165, 233, 0.25), rgba(34, 211, 238, 0.25));
    filter: blur(48px) saturate(130%);
    opacity: 0.6; pointer-events: none;
  }
  .hero{
    padding: 7rem 2rem 2rem;
    text-align: center;
  }
  .logo{
    font-family: ui-sans-serif, system-ui, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji';
    letter-spacing: 0.12em;
    font-size: clamp(42px, 9vw, 120px);
    font-weight: 800;
    margin: 0;
    background: linear-gradient(90deg, #9bd3ff, #a58bff, #7ef7ff 70%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    text-shadow: 0 0 18px rgba(130,247,255,0.25);
    cursor: pointer;
  }
  .tag{
    opacity: 0.8;
    margin: 0.5rem 0 0;
    letter-spacing: 0.08em;
  }
  .cta{ display:flex; justify-content:center; padding: 3rem 0 6rem; }
  .caw{
    appearance:none; border:1px solid rgba(130,247,255,0.35); color:var(--ink);
    background: linear-gradient(180deg, rgba(130,247,255,0.07), rgba(255,255,255,0.02));
    padding: .8rem 1.2rem; border-radius: 999px; letter-spacing: 0.06em;
    backdrop-filter: blur(6px);
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.04), 0 6px 30px rgba(0,0,0,0.4);
  }
  .coming{ max-width: 820px; margin: 0 auto; padding: 1rem 2rem 2rem; text-align: center; }
  .coming h2{ font-size: clamp(28px, 6vw, 48px); margin: 0 0 .3rem; letter-spacing: .06em; }
  .features{ display:grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 1rem; max-width: 1100px; margin: 1.5rem auto 5rem; padding: 0 1rem; }
  .feature{ padding: 1rem; border-radius: 16px; border: 1px solid rgba(130,247,255,0.2); background: linear-gradient(180deg, rgba(130,247,255,0.05), rgba(255,255,255,0.02)); }
  .feature h3{ margin: .2rem 0 .4rem; letter-spacing: .04em; }
  @media (max-width: 900px){ .features{ grid-template-columns: 1fr } }
</style>
