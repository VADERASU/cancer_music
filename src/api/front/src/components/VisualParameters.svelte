<script>
    import {
        colorNotes,
        modifyAlpha,
        modifySize,
        modifyAngle,
        blur,
        erode,
        shadow,
    } from "../api/fx.js";

    export let vis;
    let selected;
    let values = {
        insertion: {},
        transposition: {},
        deletion: {},
        inversion: {},
        translocation: {},
    };

    const modifyValue = (selected, val, func, e, args) => {
        const visuals = vis[selected];
        const use = args ? { ...args, val: e } : e;
        visuals[val] = func(use);
        vis = { ...vis };

        const value = values[selected];
        value[val] = e;
        values = { ...values };
    };

    const getValue = (val, selected, d) =>
        values[selected][val] ? values[selected][val] : d;
</script>

<div class="stack">
    <div class="hStack">
        {#each Object.keys(vis) as m}
            <button on:click={() => (selected = m)}>{m}</button>
        {/each}
    </div>
    {#if selected}
        {#key selected}
            <span>{selected}</span>
            <div class="container">
                <label for="color">Color</label><input
                    type="color"
                    name="color"
                    on:change={(e) =>
                        modifyValue(
                            selected,
                            "color",
                            colorNotes,
                            e.target.value
                        )}
                    value={getValue("color", selected, "black")}
                />
            </div>
            <div class="container">
                <label for="trans">Transparency</label><input
                    type="number"
                    step="0.1"
                    name="trans"
                    min="0"
                    max="1"
                    on:change={(e) =>
                        modifyValue(
                            selected,
                            "transparency",
                            modifyAlpha,
                            e.target.value
                        )}
                    value={getValue("transparency", selected, 1)}
                />
            </div>
            <div class="container">
                <label for="size">Size</label><input
                    type="number"
                    name="size"
                    step="1"
                    min="1"
                    on:change={(e) =>
                        modifyValue(
                            selected,
                            "size",
                            modifySize,
                            e.target.value
                        )}
                    value={getValue("size", selected, 1)}
                />
            </div>
            <div class="container">
                <label for="angle">Angle</label><input
                    type="number"
                    name="size"
                    step="1"
                    min="-180"
                    max="180"
                    on:change={(e) =>
                        modifyValue(
                            selected,
                            "angle",
                            modifyAngle,
                            e.target.value
                        )}
                    value={getValue("angle", selected, 0)}
                />
            </div>
            <div class="container">
                <label for="blur">Blur</label><input
                    type="range"
                    min={0}
                    max={5}
                    on:change={(e) =>
                        modifyValue(selected, "blur", blur, e.target.value, {
                            id: selected,
                        })}
                    value={getValue("blur", selected, 0)}
                />
            </div>
            <div class="container">
                <label for="erode">Erode</label><input
                    type="range"
                    min={0}
                    max={5}
                    on:change={(e) =>
                        modifyValue(selected, "erode", erode, e.target.value, {
                            id: selected,
                        })}
                    value={getValue("erode", selected, 0)}
                />
            </div>
            <div class="container">
                <label for="shadow">Shadow</label><input
                    type="range"
                    min={0}
                    max={20}
                    on:change={(e) =>
                        modifyValue(
                            selected,
                            "shadow",
                            shadow,
                            e.target.value,
                            {
                                id: selected,
                            }
                        )}
                    value={getValue("shadow", selected, 0)}
                />
            </div>
        {/key}
    {/if}
</div>

<style>
    .stack {
        flex-direction: column;
        display: flex;
    }
    .hStack {
        display: flex;
        gap: 5px;
    }
    .container {
        display: flex;
        justify-content: space-between;
    }
</style>
