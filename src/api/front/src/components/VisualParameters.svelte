<script>
    import { colorNotes, modifyAlpha, modifySize } from "../api/fx.js";
    export let vis;
    let selected;
    let values = {
        insertion: {},
        transposition: {},
        deletion: {},
        inversion: {},
        translocation: {},
    };

    const modifyValue = (selected, val, func, e) => {
        const visuals = vis[selected];
        visuals[val] = func(e.target.value);
        vis = { ...vis };

        const value = values[selected];
        value[val] = e.target.value;
        values = { ...values };
    };

    const getValue = (val, selected, d) =>
        values[selected][val] ? values[selected][val] : d;
</script>

{#each Object.keys(vis) as m}
    <button on:click={() => (selected = m)}>{m}</button>
{/each}
<br />

{#if selected}
    {#key selected}
        <span>{selected}</span>
        <span>Color</span><input
            type="color"
            on:change={(e) => modifyValue(selected, "color", colorNotes, e)}
            value={getValue("color", selected, "black")}
        />
        <span>Transparency</span><input
            type="number"
            step="0.1"
            min="0"
            max="1"
            on:change={(e) =>
                modifyValue(selected, "transparency", modifyAlpha, e)}
            value={getValue("transparency", selected, 1)}
        />
        <span>Size</span><input
            type="number"
            step="1"
            min="1"
            on:change={(e) => modifyValue(selected, "size", modifySize, e)}
            value={getValue("size", selected, 1)}
        />
    {/key}
{/if}

<style>
</style>
