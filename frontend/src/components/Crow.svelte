// Crow.svelte
// A Svelte component that loads an SVG crow, sets up its rig, and provides interactivity.

<script>
  import { onMount } from 'svelte';
  import { createCrowRig } from '../lib/crowRig.js';
  export let src = '/corvid_crow_anim_v9.svg';   // path to your latest SVG
  export let onReady = () => {};                  // callback exposes the rig API

  let host, audioEl, rig;

  onMount(async () => {
    const svgText = await fetch(src).then(r => r.text());
    host.innerHTML = svgText;                     // inject inline so CSS/JS can target IDs
    rig = createCrowRig(host, audioEl);
    onReady(rig);
  });

  // optional UX: quick ambient behavior
  async function ambient() {
    if (!rig) return;
    await rig.cancel?.();
    await rig.reset?.();
    await rig.blink();
    if (Math.random() < 0.3) await rig.caw();
    await rig.reset?.();
  }

  // Optional: expose a unified action runner mirroring App.svelte
  export async function run(action){
    if (!rig) return;
    try {
      await rig.cancel?.();
      await rig.reset?.();
      if (action === 'caw') {
        try { audioEl.currentTime = 0; await audioEl.play?.(); } catch {}
        await rig.caw?.();
      } else if (typeof rig?.[action] === 'function') {
        await rig[action]();
      }
    } finally {
      await rig.reset?.();
    }
  }
</script>

<div class="crow" bind:this={host} on:mouseenter={ambient}></div>
<audio bind:this={audioEl} preload="auto">
  <source src="/crow-caw.wav" type="audio/wav" />
  <source src="/crow-caw.mp3" type="audio/mpeg" />
  <!-- both provided for broader codec support -->
</audio>
<style>.crow{display:inline-block;}</style>
