<script>
  import { onMount } from "svelte";
  import { parseMXL } from "../api/parser";

  export let musicxml;
  let container;

  onMount(() => {
    parseMXL(musicxml).then((sheet) => {
      console.log(sheet);
      // sourcemeasures gives you # measures
      // in each sourceMeasure there is activeTimeSignature giving you time
      // vertical measure list gives you each part
      // vf voices is voices per measure
      // tickables.keys & .duration is the note value
    });
  });
</script>

<svg class="w-11/12 mx-auto max-h-screen" bind:this={container} >
  <rect width="100" height="100" />
</svg>

<style>
</style>
