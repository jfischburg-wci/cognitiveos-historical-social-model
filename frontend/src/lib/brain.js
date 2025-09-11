// Replace the body of decide() with your LLM provider call.
// Return a JSON object: { actions: [{type: 'caw'|'blink'|'hop'|'preen'|'headBob', ms?: number}, ...] }
export async function decide(state) {
  // Example local rules (stub) — swap with your LLM call:
  if (state.event === 'click') return { actions: [{ type: 'caw' }, { type: 'headBob', ms: 1200 }] };
  if (state.event === 'move')  return Math.random() < 0.05 ? { actions: [{ type: 'blink' }] } : { actions: [] };

  // Example shape for a real LLM call:
  // const res = await fetch('/api/crow-brain', { method:'POST', headers:{'Content-Type':'application/json'},
  //   body: JSON.stringify({ state, schema: { actions:[{type:'string', enum:['caw','blink','hop','preen','headBob']}]} }) });
  // return await res.json();

  return { actions: [] };
}
