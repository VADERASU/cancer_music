<script>
  export let text;
  export let val;
</script>

<div class="flex gap-2">
  <label class="grow" for="slider"> {text}: <b>{Math.round(val * 100)}%</b></label>
  <input
    type="range"
    name="slider"
    min="0"
    max="1"
    step="0.05"
    bind:value={val}
  />
</div>

<style>
</style>
