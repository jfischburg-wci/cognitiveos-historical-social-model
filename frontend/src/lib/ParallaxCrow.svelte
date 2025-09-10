<script>
  import { onMount, onDestroy, createEventDispatcher } from 'svelte'
  import { fly, scale } from 'svelte/transition'
  export let reducedMotion = false
  const dispatch = createEventDispatcher()
  let y = 0
  const handle = () => { y = window.scrollY || 0 }
  let idleTimer
  onMount(() => {
    handle();
    window.addEventListener('scroll', handle, { passive: true })
    // gentle idle hops periodically (no sound) when motion allowed
    if (!effectiveReduced) scheduleIdle()
  })
  onDestroy(() => { window.removeEventListener('scroll', handle); if (idleTimer) clearTimeout(idleTimer) })
  const prefersReduced = typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches
  $: effectiveReduced = reducedMotion || prefersReduced
  $: mult = effectiveReduced ? 0.02 : 0.08
  $: depth1 = Math.min(40, y * mult)
  $: depth2 = Math.min(80, y * mult * 2)
  $: depth3 = Math.min(120, y * mult * 3)

  function scheduleIdle(){
    const next = 4500 + Math.random()*3500
    idleTimer = setTimeout(() => { hop(false); scheduleIdle() }, next)
  }

  let hopping = false
  function hop(withSound = true){
    if (hopping) return
    hopping = true
    if (withSound) dispatch('interact')
    setTimeout(() => { hopping = false }, 500)
  }
</script>

<section class="stage" aria-label="Parallax crow">
  <div class="layer l1" style="transform: translate3d(0,{depth1}px,0);" aria-hidden="true" />
  <div class="layer l2" style="transform: translate3d(0,{depth2}px,0);" aria-hidden="true" />
  <!-- Shadow under the crow -->
  <div class="shadow {hopping ? 'squash' : ''}" aria-hidden="true"></div>
  <div class="crow {hopping ? 'hop' : 'idle'}" in:scale={{ start: 0.9, duration: 700 }} tabindex="0" role="button" aria-label="Crow" on:click={() => hop(true)} on:keydown={(e)=> (e.key==='Enter'||e.key===' ') && (e.preventDefault(), hop(true))}>
    <svg viewBox="0 0 340 220" width="100%" height="100%" role="img" aria-label="Crow silhouette">
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
      <!-- High-contrast full crow silhouette (approximate) -->
      <g transform="translate(30,40)" fill="#0b0f14" stroke="#000" stroke-opacity=".35" stroke-width="0.6">
        <!-- tail -->
        <path d="M10,110 C32,100 50,95 70,100 L30,128 Z" />
        <!-- body -->
        <path d="M40,90 C40,52 98,22 170,34 C228,44 268,80 268,112 C268,146 204,164 144,156 C88,148 40,126 40,90 Z" />
        <!-- wing (independent for flick) -->
        <path class="wing" d="M96,78 C136,58 174,58 210,78 C190,86 172,100 126,106 Z" fill="#0c1218" />
        <!-- legs -->
        <path d="M140,156 l-8,26" stroke="#0e0e0e" stroke-width="3" />
        <path d="M172,156 l-6,24" stroke="#0e0e0e" stroke-width="3" />
        <!-- head group with eye -->
        <g class="head">
          <circle cx="232" cy="64" r="22" fill="#0a0d12" />
          <circle class="eye" cx="238" cy="60" r="4" fill="#e6f6ff" />
        </g>
        <!-- beak -->
        <polygon points="250,62 312,50 248,78" fill="#0e1216" />
      </g>
    </svg>
  </div>
  <div class="layer l3" style="transform: translate3d(0,{depth3}px,0);" aria-hidden="true" />
</section>

<style>
  .stage{ position: relative; height: 70vh; max-width: 1100px; margin: 0 auto; }
  .layer{ position:absolute; inset: auto 0; height: 30vh; filter: blur(40px); opacity: 0.45; }
  .l1{ top: 5%; background: radial-gradient(600px 120px at 20% 50%, rgba(126,247,255,.12), transparent 60%); }
  .l2{ top: 20%; background: radial-gradient(600px 120px at 80% 50%, rgba(165,139,255,.12), transparent 60%); }
  .l3{ top: 35%; background: radial-gradient(800px 140px at 50% 50%, rgba(94,234,212,.12), transparent 60%); }
  .shadow{ position:absolute; left:50%; transform:translateX(-50%); bottom:12%; width:min(60%,620px); height:22px; background: radial-gradient(50% 50% at 50% 50%, rgba(0,0,0,.5), rgba(0,0,0,0)); filter: blur(8px); opacity:.55 }
  .crow{ position: relative; margin: 0 auto; width: min(90%, 920px); filter: drop-shadow(0 30px 60px rgba(0,0,0,0.45)); }
  .crow.idle{ animation: bob 6s ease-in-out infinite; }
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
  .shadow.squash{ animation: squash 480ms cubic-bezier(.2,.7,0,1) 1; }
  @keyframes hop{
    0% { transform: translateY(0) scale(1) }
    25% { transform: translateY(-16px) scale(1.02) }
    55% { transform: translateY(0) scale(0.985) }
    100% { transform: translateY(0) scale(1) }
  }
  @keyframes bob{
    0%,100% { transform: translateY(0) }
    50% { transform: translateY(-4px) }
  }
  @keyframes squash{
    0% { transform: translateX(-50%) scaleX(1) scaleY(1); opacity:.55 }
    25% { transform: translateX(-50%) scaleX(0.9) scaleY(0.8); opacity:.45 }
    55% { transform: translateX(-50%) scaleX(1.15) scaleY(0.6); opacity:.6 }
    100% { transform: translateX(-50%) scaleX(1) scaleY(1); opacity:.55 }
  }
  /* Wing flick on hop */
  .crow.hop .wing{ animation: wingflick 320ms ease-out 1 }
  @keyframes wingflick{
    0% { transform: rotate(0deg); transform-origin: 90px 58px }
    25% { transform: rotate(-16deg) }
    60% { transform: rotate(8deg) }
    100% { transform: rotate(0deg) }
  }
</style>
