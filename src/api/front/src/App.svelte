<script>
    import Parameters from "./components/Parameters.svelte";
    import SheetDisplay from "./components/SheetDisplay.svelte";
    import VisualParameters from "./components/VisualParameters.svelte";
    import { fade } from "svelte/transition";

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
        };
        showParams = false;
    }
</script>

<main>
    <h1 on:click={() => (showParams = true)}>Capturing Cancer with Music</h1>
    {#if showParams}
        <div transition:fade>
            <Parameters bind:mutant />
        </div>
    {/if}
    {#if mutant}
        {#key mutant}
            <VisualParameters bind:vis />
            <SheetDisplay musicxml={mutant} {vis} />
        {/key}
    {/if}
</main>

<style>
</style>
