<script>
  export let muted = false
  export let volume = 0.8
  export let reduceMotion = false
  let open = false
</script>

<div class="panel {open ? 'open' : ''}">
  <button class="toggle" aria-expanded={open} aria-controls="settings" on:click={() => open = !open}>
    ⚙️
  </button>
  <div id="settings" class="sheet" hidden={!open}>
    <div class="row">
      <label>
        <input type="checkbox" bind:checked={muted} />
        Mute
      </label>
    </div>
    <div class="row">
      <label for="vol">Volume</label>
      <input id="vol" type="range" min="0" max="1" step="0.05" bind:value={volume} />
      <span class="val">{Math.round(volume*100)}%</span>
    </div>
    <div class="row">
      <label>
        <input type="checkbox" bind:checked={reduceMotion} />
        Reduce motion
      </label>
    </div>
  </div>
</div>

<style>
  .panel{ position: fixed; right: 14px; bottom: 14px; z-index: 40 }
  .toggle{ background: rgba(0,0,0,0.45); color:#cfefff; border:1px solid rgba(130,247,255,0.35); border-radius: 999px; width:42px; height:42px; cursor: pointer }
  .sheet{ position: absolute; right: 0; bottom: 56px; min-width: 220px; padding: 10px 12px; background: rgba(13,17,23,0.9); border:1px solid rgba(130,247,255,0.2); border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.4); color: #e6eef7 }
  .row{ display:flex; align-items:center; gap: 8px; margin: 6px 0 }
  label{ font-size: 14px; opacity:.9 }
  input[type="range"]{ flex: 1 }
  .val{ font-variant-numeric: tabular-nums; opacity:.8; width: 3ch; text-align:right }
</style>

