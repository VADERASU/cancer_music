<script>
    import { colorNotes } from "../api/fx.js";
    export let vis;
    let selected;
    let values = {
        insertion: {},
        transposition: {},
        deletion: {},
        inversion: {},
        translocation: {},
    };
</script>

{#each Object.keys(vis) as m}
    <button on:click={() => (selected = m)}>{m}</button>
{/each}
<br />
{#if selected}
    <span>{selected}</span>
    <span>Color</span><input
        type="color"
        on:change={(e) => {
            const visuals = vis[selected];
            visuals["color"] = colorNotes(e.target.value);
            vis = { ...vis };

            const value = values[selected];
            value["color"] = e.target.value;
            values = { ...values };
        }}
        value={values[selected]["color"] ? values[selected]["color"] : "black"}
    />
{/if}

<style>
</style>
