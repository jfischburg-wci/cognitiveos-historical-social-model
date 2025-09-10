<script>
  import { onMount, onDestroy, createEventDispatcher } from 'svelte'
  import { fly, scale } from 'svelte/transition'
  const dispatch = createEventDispatcher()
  let y = 0
  const handle = () => { y = window.scrollY || 0 }
  onMount(() => { handle(); window.addEventListener('scroll', handle, { passive: true }) })
  onDestroy(() => window.removeEventListener('scroll', handle))
  const prefersReduced = typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches
  $: mult = prefersReduced ? 0.02 : 0.08
  $: depth1 = Math.min(40, y * mult)
  $: depth2 = Math.min(80, y * mult * 2)
  $: depth3 = Math.min(120, y * mult * 3)

  let hopping = false
  function triggerHop(){
    if (hopping) return
    hopping = true
    dispatch('interact')
    setTimeout(() => { hopping = false }, 500)
  }
</script>

<section class="stage" aria-label="Parallax crow">
  <div class="layer l1" style="transform: translate3d(0,{depth1}px,0);" aria-hidden="true" />
  <div class="layer l2" style="transform: translate3d(0,{depth2}px,0);" aria-hidden="true" />
  <div class="crow {hopping ? 'hop' : ''}" in:scale={{ start: 0.9, duration: 700 }} tabindex="0" role="button" aria-label="Crow" on:click={triggerHop} on:keydown={(e)=> (e.key==='Enter'||e.key===' ') && (e.preventDefault(), triggerHop())}>
    <svg viewBox="0 0 240 140" width="100%" height="100%" role="img" aria-label="Crow silhouette">
      <defs>
        <linearGradient id="iris" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#7ef7ff" />
          <stop offset="50%" stop-color="#a58bff" />
          <stop offset="100%" stop-color="#5eead4" />
        </linearGradient>
        <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur in="SourceGraphic" stdDeviation="1.2" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      <!-- Stylized crow-ish silhouette -->
      <g transform="translate(20,20)" fill="#0f1216">
        <path d="M0,40 C20,10 80,0 120,20 C150,35 160,60 160,80 L120,70 L70,65 L40,70 Z" fill="url(#iris)" opacity="0.25"/>
        <path d="M0,40 C20,10 80,0 120,20 C150,35 160,60 160,80 L120,70 L70,65 L40,70 Z" />
        <!-- head -->
        <g class="head">
          <circle cx="145" cy="45" r="18" fill="#0b0e12" />
          <!-- eye -->
          <circle class="eye" cx="150" cy="43" r="3.6" fill="#cde8ff" />
        </g>
        <!-- beak -->
        <polygon points="160,45 200,38 158,52" fill="#101418" />
      </g>
    </svg>
  </div>
  <div class="layer l3" style="transform: translate3d(0,{depth3}px,0);" aria-hidden="true" />
</section>

<style>
  .stage{ position: relative; height: 60vh; max-width: 1100px; margin: 0 auto; }
  .layer{ position:absolute; inset: auto 0; height: 30vh; filter: blur(40px); opacity: 0.45; }
  .l1{ top: 5%; background: radial-gradient(600px 120px at 20% 50%, rgba(126,247,255,.12), transparent 60%); }
  .l2{ top: 20%; background: radial-gradient(600px 120px at 80% 50%, rgba(165,139,255,.12), transparent 60%); }
  .l3{ top: 35%; background: radial-gradient(800px 140px at 50% 50%, rgba(94,234,212,.12), transparent 60%); }
  .crow{ position: relative; margin: 0 auto; width: min(90%, 920px); filter: drop-shadow(0 30px 60px rgba(0,0,0,0.45)); }
  .eye{ animation: blink 6s infinite steps(1); transform-origin: center; filter: url(#glow); }
  @keyframes blink{
    0%, 92%, 100% { r: 3.6 }
    94%, 96% { r: 0.8 }
  }
  /* Idle head tilt */
  .head{ transform-origin: 145px 45px; animation: headtilt 5.5s ease-in-out infinite; }
  @keyframes headtilt{
    0%, 90%, 100% { transform: rotate(0deg) }
    40% { transform: rotate(2.2deg) }
    50% { transform: rotate(-1.5deg) }
    60% { transform: rotate(1.2deg) }
  }
  /* Hop interaction */
  .crow.hop{ animation: hop 480ms cubic-bezier(.2,.7,0,1) 1; }
  @keyframes hop{
    0% { transform: translateY(0) scale(1) }
    35% { transform: translateY(-12px) scale(1.02) }
    70% { transform: translateY(0) scale(0.98) }
    100% { transform: translateY(0) scale(1) }
  }
</style>
