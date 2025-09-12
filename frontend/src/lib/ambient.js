// Weighted, jittered ambient behaviors for the crow.
// Usage: const ambient = startAmbient({ rig, el, caw, reduceMotion });
//        ambient.stop()

export function startAmbient({ rig, el, caw, reduceMotion = false }) {
  let stopped = false;
  let cooldown = 0;        // ms left before another action may run
  let pauseUntil = 0;      // ms timestamp after user interaction
  let raf = null;

  // Position and direction for bounded traversal
  let dir = 1;  // 1 = right, -1 = left
  let x = 0;    // current translateX in px

  // Actions (weights tune relative frequency)
  const actions = [
    { name: 'blink',   run: () => rig.blink(),                   weight: 4, cool: 900  },
    { name: 'headBob', run: () => rig.headBob(),                 weight: 3, cool: 1300 },
    { name: 'preen',   run: () => rig.preen(),                   weight: 2, cool: 2500 },
    { name: 'caw',     run: async () => { await rig.caw(); await caw?.(); }, weight: 2, cool: 1200 },
    { name: 'hop',     run: () => hopAcrossAndBack(el, rig),     weight: 2, cool: 2000 },
    { name: 'walk',    run: () => rig.walk(),                    weight: 1, cool: 3000 },
  ];

  // Hop across and back: multiple hops with bounded drift & direction flips
  async function hopAcrossAndBack(el, rig) {
    const rect = el.getBoundingClientRect();
    const vw = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
    const margin = 24; // keep away from edges
    const max = Math.max(0, vw - rect.width - margin);
    const hops = 2 + Math.floor(Math.random() * 3); // 2–4 hops

    for (let i = 0; i < hops; i++) {
      const step = 22 + Math.random() * 6; // px per hop
      x += dir * step;
      if (x < 0) { x = 0; dir = 1; }
      if (x > max) { x = max; dir = -1; }

      // visually drift while the hop animation runs (WAAPI)
      const anim = el.animate(
        [{ transform: `translateX(${x - dir * step}px)` }, { transform: `translateX(${x}px)` }],
        { duration: 900, easing: 'cubic-bezier(.3,.6,.3,1)', fill: 'forwards' }
      );
      anim.commitStyles?.();
      await rig.hop();
    }
  }

  // Pick an action by weight
  function pick() {
    const pool = actions.flatMap(a => Array(a.weight).fill(a));
    return pool[Math.floor(Math.random() * pool.length)];
  }

  // Ambient loop with visibility & interaction guards
  function tick() {
    if (stopped) return;
    raf = requestAnimationFrame(tick);

    if (document.hidden) return;
    if (Date.now() < pauseUntil) return;

    if (cooldown > 0) { cooldown -= 16; return; }

    // ~0.8% chance per frame → every few seconds in practice
    if (Math.random() < 0.008) {
      const a = pick();
      cooldown = a.cool + 400 + Math.random() * 600; // jitter
      a.run().catch(() => {});
    }
  }

  // Respect reduced motion
  if (!reduceMotion) {
    raf = requestAnimationFrame(tick);

    // User interaction pauses ambient a bit
    const pause = () => { pauseUntil = Date.now() + 1800; };
    el.addEventListener('pointermove', pause);
    el.addEventListener('pointerdown', pause);
    el.addEventListener('keydown', pause);

    return {
      stop() {
        stopped = true;
        if (raf) cancelAnimationFrame(raf);
        el.removeEventListener('pointermove', pause);
        el.removeEventListener('pointerdown', pause);
        el.removeEventListener('keydown', pause);
      }
    };
  }

  // Reduced motion → no-op handle
  return { stop() {} };
}
