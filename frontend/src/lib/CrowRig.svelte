<script>
  import { createEventDispatcher, onMount, onDestroy } from 'svelte';
  export let src = '/corvid_crow_anim_v9.svg';
  export const reduceMotion = false;

  const dispatch = createEventDispatcher();
  let host, svg;

  // Helper to add an animation class and remove it after a duration
  const once = (cls, ms) =>
    new Promise((resolve) => {
      if (!svg) return resolve();
      svg.classList.add(cls);
      setTimeout(() => {
        svg.classList.remove(cls);
        resolve();
      }, ms);
    });

  // Exposed one-shot actions
  function blink()   { return once('animate-blink', 240); }
  function caw()     { return once('animate-caw', 600); }
  function headBob() { return once('animate-headBob', 1200); }
  function preen()   { return once('animate-preen', 2400); }
  function hop()     { dispatch('interact'); return once('animate-hop', 900); }

  // Remove hairline seams between eye and wing by nudging masked groups
  function nudgeSeams() {
    const nudge = (id, dx = 0, dy = 0) => {
      const g = svg?.getElementById(id);
      if (g) {
        const prev = g.getAttribute('transform') || '';
        g.setAttribute('transform', `${prev} translate(${dx},${dy})`);
      }
    };
    nudge('Head', -0.35, 0);
    nudge('Neck', -0.20, 0);
    nudge('Body',  0.35, 0);
    nudge('Wing',  0,   -0.15);
    nudge('Tail', -0.25, 0);
    nudge('Legs',  0.15, 0);
    nudge('Feet',  0.15, 0);
  }

  // Ensure eyelid groups exist for blink to work
  function ensureIds() {
    if (!svg) return;
    const up = svg.getElementById('EyelidUpper');
    const lo = svg.getElementById('EyelidLower');
    if (up && lo && !svg.getElementById('Eyelids')) {
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      g.setAttribute('id', 'Eyelids');
      up.parentNode.insertBefore(g, up);
      g.appendChild(up);
      g.appendChild(lo);
    }
  }

  // Trigger caw on custom window event
  function onCawEvent() {
    caw();
  }

  onMount(async () => {
    const text = await fetch(src).then((r) => r.text());
    host.innerHTML = text;
    svg = host.querySelector('svg') || host.firstElementChild;
    ensureIds();
    nudgeSeams();

    // Dispatch ready event with API for parent
    dispatch('ready', { api: { blink, caw, headBob, preen, hop } });

    window.addEventListener('corvid-caw', onCawEvent);
  });

  onDestroy(() => {
    window.removeEventListener('corvid-caw', onCawEvent);
  });
</script>

<div class="crow" bind:this={host} aria-label="Crow rig"></div>

<style>
  .crow :global(.rig),
  .crow :global([id]) {
    transform-box: fill-box;
  }
</style>
