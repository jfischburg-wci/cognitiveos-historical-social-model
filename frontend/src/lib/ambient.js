// Weighted, jittered ambient behaviors for the crow.
// Usage: const ambient = startAmbient({ rig, el, caw, reduceMotion });
//        ambient.stop()

export function startAmbient({ rig, el, caw, reduceMotion = false }){
  let stopped = false;
  let cooldown = 0;        // ms left before another action may run
  let pauseUntil = 0;      // ms timestamp after user interaction
  let raf = null;

  // Actions we can choose from
  const actions = [
    { name:'blink',   run: () => rig.blink(),          weight: 4, cool: 1000 },
    { name:'headBob', run: () => rig.headBob(),        weight: 3, cool: 1400 },
    { name:'preen',   run: () => rig.preen(),          weight: 2, cool: 2600 },
    { name:'caw',     run: async () => { await rig.caw(); await caw?.(); }, weight: 2, cool: 1200 },
    { name:'hop',     run: () => hopAcross(el, rig),   weight: 2, cool: 2000 },
  ];

  // Hop across the screen = a few hops with slight forward drift (WAAPI on wrapper)
  async function hopAcross(el, rig){
    const hops = 2 + Math.floor(Math.random()*3); // 2–4 hops
    for (let i=0;i<hops;i++){
      // drift ~22–28px per hop
      const dx = 22 + Math.random()*6;
      el.animate([{ transform:'translateX(0)'},{ transform:`translateX(${dx}px)`}],
                 { duration: 900, easing:'cubic-bezier(.3,.6,.3,1)' }).commitStyles?.();
      await rig.hop();
    }
  }

  // Pick one by weight
  function pick(){
    const pool = actions.flatMap(a => Array(a.weight).fill(a));
    return pool[Math.floor(Math.random()*pool.length)];
  }

  // Ambient loop with visibility / interaction guards
  function tick(ts){
    if (stopped) return;
    raf = requestAnimationFrame(tick);

    // Pause when tab is hidden or just after interaction
    if (document.hidden) return;
    if (Date.now() < pauseUntil) return;

    // Cooldown countdown
    if (cooldown > 0) { cooldown -= 16; return; }

    // Randomly decide whether to fire this frame (low probability → natural spacing)
    if (Math.random() < 0.008) {             // ~0.8% chance per frame (~ every few seconds)
      const a = pick();
      cooldown = a.cool + 400 + Math.random()*600; // add jitter
      a.run().catch(()=>{});
    }
  }

  // Respect reduced motion
  if (!reduceMotion){
    raf = requestAnimationFrame(tick);

    // User interaction pauses ambient for a bit
    const pause = () => { pauseUntil = Date.now() + 1800; };
    el.addEventListener('pointermove', pause);
    el.addEventListener('pointerdown', pause);
    el.addEventListener('keydown', pause);

    return {
      stop(){
        stopped = true;
        if (raf) cancelAnimationFrame(raf);
        el.removeEventListener('pointermove', pause);
        el.removeEventListener('pointerdown', pause);
        el.removeEventListener('keydown', pause);
      }
    };
  }

  // Reduced motion → provide a no-op handle
  return { stop(){ /* noop */ } };
}