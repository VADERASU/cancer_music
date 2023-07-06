<script>
  export let onClick;
  export let label;

  export let toggled = false;

  $: css = toggled ? "selected" : "";
</script>

<button class={`default-button ${css}`} on:click={onClick}>{label}</button>

<style lang="postcss">
  .selected {
    background-color: black;
    color: white;
  }
</style>
