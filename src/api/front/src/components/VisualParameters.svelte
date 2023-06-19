<script>
    import { colorNotes } from "../api/fx.js";
    export let vis;
    let selected;
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
        }}
        value={vis[selected]["color"] ? vis[selected]["color"] : "black"}
    />
{/if}

<style>
</style>
