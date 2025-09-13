// crowRig.js
// Provides an interface to control crow animations and sounds via CSS classes.

export function createCrowRig(rootEl, audioEl) {
  const runOnce = (cls, ms) =>
    new Promise(r => { rootEl.classList.add(cls); setTimeout(() => { rootEl.classList.remove(cls); r(); }, ms); });

  const loops = new Set();
  const startLoop = cls => { rootEl.classList.add(cls); loops.add(cls); return () => stopLoop(cls); };
  const stopLoop  = cls => { rootEl.classList.remove(cls); loops.delete(cls); };
  const stopAll   = () => [...loops].forEach(stopLoop);

  const clearPlays = () => {
    rootEl.className.split(/\s+/).forEach(c => { if (c.startsWith('play-') || c.startsWith('animate-')) rootEl.classList.remove(c); });
  };

  async function cancel(){ stopAll(); clearPlays(); }
  async function reset(){ await cancel(); }

  return {
    // one-shots
    blink: () => runOnce('play-blink', 240),
    caw:   () => { audioEl && (audioEl.currentTime = 0, audioEl.play()); return runOnce('play-caw', 600); },

    // loops
    headBobStart: () => startLoop('loop-headBob'),
    preenStart:   () => startLoop('loop-preen'),
    hopStart:     () => startLoop('loop-hop'),
    // walking loop helpers
    walkStart:    () => startLoop('loop-walk'),
    headBobStop:  () => stopLoop('loop-headBob'),
    preenStop:    () => stopLoop('loop-preen'),
    hopStop:      () => stopLoop('loop-hop'),
    walkStop:     () => stopLoop('loop-walk'),
    stopAll,
    cancel,
    reset
  };
}
