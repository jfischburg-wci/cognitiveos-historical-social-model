<script>
  import { Motion } from '@motionone/svelte'
  import ParallaxCrow from './lib/ParallaxCrow.svelte'
  let audio
  function caw() {
    if (audio && audio.play) {
      audio.currentTime = 0
      audio.play().catch(() => {})
    }
  }
</script>

<Motion
  initial={{ opacity: 0, y: 24 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.7 }}
  class="page"
>
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

  <!-- Optional: place crow-caw.mp3 into frontend/public/ to enable -->
  <audio bind:this={audio} src="/crow-caw.mp3" preload="auto" />
</Motion>

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
</style>

