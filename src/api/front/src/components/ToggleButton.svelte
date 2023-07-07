<script>
  export let onClick;
  export let label;

  export let toggled = false;

  $: css = toggled ? "selected" : "";
</script>

<button class={`default-button ${css}`} on:click={onClick}>{label}</button>

<style lang="postcss">
  .selected {
    @apply bg-gray-950 text-white;
  }
</style>
