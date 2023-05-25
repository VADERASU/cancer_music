<script>
    import Parameters from "./Parameters.svelte";
    import SheetDisplay from "./SheetDisplay.svelte";
    let mutant;
</script>

<main>
    <h1>Capturing Cancer with Music</h1>
    <Parameters bind:mutant />
    {#if mutant}
        <SheetDisplay musicxml={mutant} />
    {/if}
</main>

<style>
</style>
