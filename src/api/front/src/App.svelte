<script>
    import Parameters from "./Parameters.svelte";
    import SheetDisplay from "./SheetDisplay.svelte";
    import VisualParameters from "./components/VisualParameters.svelte";

    let mutant;
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
    }
</script>

<main>
    <h1>Capturing Cancer with Music</h1>
    <Parameters bind:mutant />
    {#if mutant}
        {#key mutant}
            <VisualParameters bind:vis />
            <SheetDisplay musicxml={mutant} {vis} />
        {/key}
    {/if}
</main>

<style>
</style>
