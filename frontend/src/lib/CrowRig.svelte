<script>
  import { onMount, onDestroy, createEventDispatcher } from 'svelte'
  const SRC = '/corvid_crow_anim_v9.svg'
  let container
  let svg
  const dispatch = createEventDispatcher()

  // Helper: run a one-shot animation class on the root <svg>
  function run(animClass, dur = 600) {
    if (!svg) return
    svg.classList.add(animClass)
    const t = setTimeout(() => svg && svg.classList.remove(animClass), dur)
    return () => clearTimeout(t)
  }

  // Public triggers (can be called by parent if bound via bind:this)
  export function headBob() { run('animate-headBob', 1200) }
  export function blink()   { run('animate-blink', 350) }
  export function preen()   { run('animate-preen', 1800) }
  export function hop()     { run('animate-hop', 900); dispatch('interact') }
  export function caw()     { run('animate-caw', 600); dispatch('interact') }

  function onCawEvent() { caw() }

  onMount(async () => {
    try {
      const res = await fetch(SRC)
      const text = await res.text()
      container.innerHTML = text
      svg = container.querySelector('svg')
      if (svg) svg.setAttribute('role', 'img')
    } catch {}
    window.addEventListener('corvid-caw', onCawEvent)
  })
  onDestroy(() => { window.removeEventListener('corvid-caw', onCawEvent) })
</script>

<section class="stage" aria-label="Crow rig">
  <div class="crow" bind:this={container} />
</section>

<style>
  .stage{ position: relative; display:flex; justify-content:center; margin: 0 auto; }
  .crow{ width: min(90%, 920px); filter: drop-shadow(0 30px 60px rgba(0,0,0,0.45)); }
  .crow svg{ display:block; width:100%; height:auto }
</style>

