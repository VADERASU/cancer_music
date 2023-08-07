<script>
  import "./app.css";
  import Parameters from "./components/Parameters.svelte";
  import SaveToolBar from "./components/SaveToolBar.svelte";
  import SheetDisplay from "./components/SheetDisplay.svelte";

  let mutant;
  let showParams = true;
  let vis = {
    insertion: {},
    transposition: {},
    deletion: {},
    inversion: {},
    translocation: {},
  };

  // reset effects if sheet changes
  $: if (mutant) {
    vis = {
      insertion: {},
      transposition: {},
      deletion: {},
      inversion: {},
      translocation: {},
      cure: {},
    };
    showParams = false;
  }
</script>

<div class="container flex flex-col px-5 gap-2">
  <h1 class="text-3xl">Capturing Cancer with Music</h1>
  {#if showParams}
    <Parameters bind:mutant />
  {/if}
  {#if mutant}
    {#key mutant}
      <SaveToolBar musicxml={mutant} />
    {/key}
  {/if}
</div>
{#if mutant}
  {#key mutant}
    <SheetDisplay musicxml={mutant} {vis} />
  {/key}
{/if}

<style lang="postcss">
</style>
