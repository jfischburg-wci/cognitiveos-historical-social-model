<script>
  import { onMount, onDestroy, createEventDispatcher } from 'svelte'
  import { fly, scale } from 'svelte/transition'
  import traceRaw from '../assets/crow_trace.svg?raw'
  import bodyRaw from '../assets/parts/body.svg?raw'
  import beakUpperRaw from '../assets/parts/beak_upper.svg?raw'
  import beakLowerRaw from '../assets/parts/beak_lower.svg?raw'
  import wingF1Raw from '../assets/parts/wing_f1.svg?raw'
  import wingF2Raw from '../assets/parts/wing_f2.svg?raw'
  import wingF3Raw from '../assets/parts/wing_f3.svg?raw'
  import tailRaw from '../assets/parts/tail.svg?raw'
  export let reducedMotion = false
  const dispatch = createEventDispatcher()
  let y = 0
  const handle = () => { y = window.scrollY || 0 }
  let idleTimer
  let pressTimer
  let container
  // Prepare traced SVG content (from potrace)
  let traceGroup = ''
  let traceScale = 1
  let traceTx = 20, traceTy = 16
  let tracePathD = ''
  let bodyPathD = ''
  let beakUPathD = ''
  let beakLPathD = ''
  let wf1PathD = ''
  let wf2PathD = ''
  let wf3PathD = ''
  let tailPathD = ''
  {
    const vb = /viewBox="([^"]+)"/i.exec(traceRaw)
    const dims = vb ? vb[1].split(/\s+/).map(parseFloat) : [0,0,1024,1024]
    const w = dims[2] || 1024
    const desired = 330
    traceScale = desired / w
    const path = traceRaw.match(/<path[^>]*d=\"([^\"]+)\"/i)
    if (path && path[1]) tracePathD = path[1]
    const pick = (raw)=>{ const m = raw && raw.match(/<path[^>]*d=\"([^\"]+)\"/i); return m?m[1]:'' }
    bodyPathD = pick(bodyRaw)
    beakUPathD = pick(beakUpperRaw)
    beakLPathD = pick(beakLowerRaw)
    wf1PathD = pick(wingF1Raw)
    wf2PathD = pick(wingF2Raw)
    wf3PathD = pick(wingF3Raw)
    tailPathD = pick(tailRaw)
  }
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
    const next = 4000 + Math.random()*3000
    idleTimer = setTimeout(() => {
      const r = Math.random()
      if (!effectiveReduced && r < 0.22) { hop(false) }
      else if (r < 0.40) { doPreen() }
      else if (r < 0.58) { doPeck() }
      else if (r < 0.78) { doRuffle() }
      else if (r < 0.92) { doTail() }
      scheduleIdle()
    }, next)
  }

  let hopping = false
  function hop(withSound = true){
    if (hopping) return
    hopping = true
    if (withSound) dispatch('interact')
    setTimeout(() => { hopping = false }, 500)
  }

  // Interaction behaviors
  let alert = false
  let look = 0 // -1 left, 0 center, 1 right
  let preen = false
  let ruffle = false
  let peck = false
  let tail = false
  let cawOpen = false

  function toAlert(v=true){ alert = v }
  function doRuffle(){ ruffle = true; setTimeout(()=> ruffle=false, 420) }
  function doPeck(){ peck = true; setTimeout(()=> peck=false, 220) }
  function doTail(){ tail = true; setTimeout(()=> tail=false, 300) }
  function doPreen(){ preen = true; setTimeout(()=> preen=false, 700) }
  function openBeak(){ cawOpen = true; setTimeout(()=> cawOpen = false, 260) }

  function onMouseMove(e){
    if (!container) return
    const rect = container.getBoundingClientRect()
    const cx = rect.left + rect.width/2
    look = (e.clientX < cx ? -1 : 1)
  }
  function onMouseLeave(){ look = 0; toAlert(false) }
  function onMouseEnter(){ toAlert(true) }
  function onDoubleClick(){ doRuffle() }
  function onMouseDown(){
    clearTimeout(pressTimer)
    pressTimer = setTimeout(()=>{ openBeak(); hop(true) }, 300)
  }
  function onMouseUp(){ clearTimeout(pressTimer) }

  let lastScroll = 0
  function onWheel(ev){
    const now = Date.now()
    const dt = now - lastScroll
    lastScroll = now
    if (Math.abs(ev.deltaY) > 140 && dt < 200){ hop(false) }
  }

  // Listen for global caw events from App
  onMount(()=>{
    const handler = ()=> openBeak()
    window.addEventListener('corvid-caw', handler)
    return ()=> window.removeEventListener('corvid-caw', handler)
  })
</script>

<section class="stage" aria-label="Parallax crow" bind:this={container} on:mouseenter={onMouseEnter} on:mousemove={onMouseMove} on:mouseleave={onMouseLeave} on:dblclick={onDoubleClick} on:mousedown={onMouseDown} on:mouseup={onMouseUp} on:wheel|passive={onWheel}>
  <div class="layer l1" style="transform: translate3d(0,{depth1}px,0);" aria-hidden="true" />
  <div class="layer l2" style="transform: translate3d(0,{depth2}px,0);" aria-hidden="true" />
  <!-- Backplate glow for contrast -->
  <div class="backplate" aria-hidden="true"></div>
  <!-- Shadow under the crow -->
  <div class="shadow {hopping ? 'squash' : ''}" aria-hidden="true"></div>
  <div class="crow {hopping ? 'hop' : 'idle'} {cawOpen ? 'caw' : ''} {alert ? 'alert' : ''} {preen ? 'preen' : ''} {ruffle ? 'ruffle' : ''} {peck ? 'peck' : ''} look-{look}"
    in:scale={{ start: 0.9, duration: 700 }} tabindex="0" role="button" aria-label="Crow"
    on:click={() => hop(true)}
    on:keydown={(e)=> (e.key==='Enter'||e.key===' ') && (e.preventDefault(), hop(true))}>
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
        <!-- Rim light for contrast -->
        <linearGradient id="rim" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#8bf0ff" stop-opacity="0.35" />
          <stop offset="50%" stop-color="#a58bff" stop-opacity="0.3" />
          <stop offset="100%" stop-color="#7ef7ff" stop-opacity="0.35" />
        </linearGradient>
        <!-- Clip path of traced silhouette for internal layers -->
        <clipPath id="crowClip">
          <g transform="translate({traceTx},{traceTy}) scale({traceScale})">
            {#if tracePathD}
              <path d={tracePathD} />
            {/if}
          </g>
        </clipPath>
      </defs>
      <!-- Traced silhouette and clipped animation layers -->
      <g transform="translate(30,40)" fill="#0b0f14" stroke="#000" stroke-opacity=".35" stroke-width="0.6">
        <!-- silhouette render (precise body path if available) -->
        <g transform="translate({traceTx},{traceTy}) scale({traceScale})">
          {#if bodyPathD}
            <path class="sil" d={bodyPathD} />
          {:else if tracePathD}
            <path class="sil" d={tracePathD} />
          {/if}
        </g>
        <!-- layers clipped to silhouette -->
        <g clip-path="url(#crowClip)">
          <!-- wing group with layered feathers for shake/flick -->
          <g class="wing">
            {#if wf1PathD}<path class="feather f1" d={wf1PathD} fill="#0c1218" />{:else}<path class="feather f1" d="M96,78 C132,60 170,58 206,78 C188,84 168,98 126,104 Z" fill="#0c1218" />{/if}
            {#if wf2PathD}<path class="feather f2" d={wf2PathD} fill="#0c141a" />{:else}<path class="feather f2" d="M96,86 C134,66 170,66 202,84 C186,90 168,102 126,108 Z" fill="#0c141a" />{/if}
            {#if wf3PathD}<path class="feather f3" d={wf3PathD} fill="#0d151c" />{:else}<path class="feather f3" d="M98,92 C132,74 166,72 198,88 C182,94 166,106 126,112 Z" fill="#0d151c" />{/if}
          </g>
          <!-- articulating beak (split upper/lower) -->
          <g class="beak-upper">{#if beakUPathD}<path d={beakUPathD} fill="#12171d" />{/if}</g>
          <g class="beak-lower">{#if beakLPathD}<path d={beakLPathD} fill="#0d1319" />{/if}</g>
          <!-- tail (overlay for twitch) -->
          {#if tailPathD}<path class="tailpath" d={tailPathD} fill="#0b0f14" />{:else}<path class="tailpath" d="M10,110 C32,100 50,95 70,100 L30,128 Z" fill="#0b0f14" />{/if}
          <!-- legs (overlay) -->
          <path d="M140,156 l-8,26" stroke="#0e0e0e" stroke-width="3" />
          <path d="M172,156 l-6,24" stroke="#0e0e0e" stroke-width="3" />
        <!-- head group with eye (overlay) -->
        <g class="head">
          <circle cx="232" cy="64" r="22" fill="#0a0d12" />
          <circle class="eye" cx="238" cy="60" r="4" fill="#e6f6ff" />
        </g>
        <!-- beak -->
        <polygon points="250,62 312,50 248,78" fill="#0e1216" />
        </g>
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
  .shadow{ position:absolute; left:50%; transform:translateX(-50%); bottom:12%; width:min(60%,620px); height:22px; background: radial-gradient(50% 50% at 50% 50%, rgba(0,0,0,.55), rgba(0,0,0,0)); filter: blur(8px); opacity:.6 }
  .backplate{ position:absolute; left:50%; transform:translateX(-50%); bottom:20%; width:min(80%, 900px); height:38vh; background: radial-gradient(60% 45% at 50% 50%, rgba(126,247,255,.35), rgba(165,139,255,.28) 45%, rgba(14,165,233,.22) 75%, transparent 85%); filter: blur(60px) saturate(130%); opacity:.35; mix-blend-mode: screen; pointer-events:none }
  .crow{ position: relative; margin: 0 auto; width: min(90%, 920px); filter: drop-shadow(0 30px 60px rgba(0,0,0,0.45)); }
  .crow.idle{ animation: bob 6s ease-in-out infinite; }
  .crow.alert{ animation: none; transform-origin: center; animation: alertpose 220ms ease-out forwards }
  .eye{ animation: blink 6s infinite steps(1); transform-origin: center; filter: url(#glow); }
  .sil{ fill:#121c26; stroke:url(#rim); stroke-width:1.8; stroke-opacity:.9 }
  @keyframes blink{
    0%, 92%, 100% { r: 3.6 }
    94%, 96% { r: 0.8 }
  }
  /* Idle head tilt */
  .head{ transform-origin: 145px 45px; animation: headtilt 5.5s ease-in-out infinite; }
  .crow.look--1 .head{ transform: rotate(-6deg) }
  .crow.look-1 .head{ transform: rotate(6deg) }
  .crow.alert .head{ animation: none; transform: rotate(3deg) }
  .crow.preen .head{ animation: none; transform: translate(-24px,12px) rotate(-22deg) }
  .crow.peck .head{ animation: none; transform: translate(10px,12px) rotate(16deg) }
  .crow.tail .tailpath{ transform-origin: 38px 116px; animation: tailwag 300ms ease-out 1 }
  @keyframes headtilt{
    0%, 90%, 100% { transform: rotate(0deg) }
    40% { transform: rotate(2.2deg) }
    50% { transform: rotate(-1.5deg) }
    60% { transform: rotate(1.2deg) }
  }
  @keyframes tailwag{
    0% { transform: rotate(0deg) }
    30% { transform: rotate(-6deg) }
    80% { transform: rotate(2deg) }
    100% { transform: rotate(0deg) }
  }
  @keyframes alertpose{ from{ transform: translateY(-2px) scale(1.01)} to{ transform: translateY(-2px) scale(1.01)} }
  /* Hop interaction */
  .crow.hop{ animation: hop 480ms cubic-bezier(.2,.7,0,1) 1; }
  .shadow.squash{ animation: squash 480ms cubic-bezier(.2,.7,0,1) 1; }
  @keyframes hop{
    0% { transform: translateY(0) scale(1) }
    25% { transform: translateY(var(--hop-raise, -18px)) scale(1.02) }
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
  .crow.ruffle .wing{ animation: feathershake 420ms ease-out 1 }
  .crow.preen .wing{ transform-origin: 130px 90px; transform: rotate(-6deg) }
  /* Beak articulation */
  .beak-upper{ transform-origin: 236px 60px }
  .beak-lower{ transform-origin: 238px 64px }
  .crow.caw .beak-upper, .crow.hop .beak-upper{ animation: beakup 240ms ease-out 1 }
  .crow.caw .beak-lower, .crow.hop .beak-lower{ animation: beaklo 240ms ease-out 1 }
  @keyframes beakup{ 0%{ transform: rotate(0) } 40%{ transform: rotate(-12deg) } 100%{ transform: rotate(0) } }
  @keyframes beaklo{ 0%{ transform: rotate(0) } 40%{ transform: rotate(10deg) } 100%{ transform: rotate(0) } }
  .crow.hop .feather{ animation: feathershake 320ms ease-out 1 }
  .crow.idle .feather{ animation: microshake 4.5s ease-in-out infinite }
  .crow.idle .feather.f2{ animation-delay: .1s }
  .crow.idle .feather.f3{ animation-delay: .2s }
  /* Mobile tuning */
  @media (max-width: 520px){
    .stage{ height: 60vh }
    .crow{ width: min(96%, 760px) }
    :root{ --hop-raise: -11px }
    .trace *{ stroke-width: 1.2; stroke-opacity: .75 }
    .backplate{ opacity:.28; filter: blur(50px) }
  }
  @keyframes wingflick{
    0% { transform: rotate(0deg); transform-origin: 90px 58px }
    25% { transform: rotate(-16deg) }
    60% { transform: rotate(8deg) }
    100% { transform: rotate(0deg) }
  }
  @keyframes feathershake{
    0% { transform: rotate(0deg); transform-origin: 130px 90px }
    30% { transform: rotate(-8deg) }
    70% { transform: rotate(5deg) }
    100% { transform: rotate(0deg) }
  }
  @keyframes microshake{
    0%,100% { transform: rotate(0deg); transform-origin: 130px 90px }
    50% { transform: rotate(-1.4deg) }
  }
</style>
