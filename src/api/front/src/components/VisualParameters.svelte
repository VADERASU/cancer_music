<script>
  import {
    colorNotes,
    modifyAlpha,
    modifySize,
    modifyAngle,
    blur,
    erode,
    shadow,
    waves,
    applyFilter,
    shadowColor,
  } from "../api/fx";

  import SVGFilters from "./SVGFilters.svelte";

  export let vis;
  let selected;
  let values = {
    insertion: {},
    transposition: {},
    deletion: {},
    inversion: {},
    translocation: {},
  };

  const modifyValue = (which, val, func, args) => {
    const visuals = vis[which];
    visuals[val] = func(args);
    vis = { ...vis };
  };

  const updateUI = (which, val, e) => {
    const value = values[which];
    value[val] = e;
    values = { ...values };
  };

  const getValue = (val, which, d) =>
    values[which][val] ? values[which][val] : d;
</script>

<div class="stack">
  <svg width={0} height={0}>
    <defs id="defs">
      {#each Object.keys(vis) as m}
        <SVGFilters id={m} />
      {/each}
    </defs>
  </svg>
  <div class="hStack">
    {#each Object.keys(vis) as m}
      <button
        on:click={() => {
          selected = m;
        }}>{m}</button
      >
    {/each}
  </div>
  {#if selected}
    {#key selected}
      <span>{selected}</span>
      <div class="container">
        <label for="color">Color</label><input
          type="color"
          name="color"
          on:change={(e) => {
            modifyValue(selected, "color", colorNotes, e.target.value);
            updateUI(selected, "color", e.target.value);
          }}
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
          on:change={(e) => {
            modifyValue(selected, "transparency", modifyAlpha, e.target.value);
            updateUI(selected, "transparency", e.target.value);
          }}
          value={getValue("transparency", selected, 1)}
        />
      </div>
      <div class="container">
        <label for="size">Size</label><input
          type="number"
          name="size"
          step="1"
          min="1"
          on:change={(e) => {
            modifyValue(selected, "size", modifySize, e.target.value);
            updateUI(selected, "size", e.target.value);
          }}
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
          on:change={(e) => {
            modifyValue(selected, "angle", modifyAngle, e.target.value);
            updateUI(selected, "angle", e.target.value);
          }}
          value={getValue("angle", selected, 0)}
        />
      </div>
      <div class="container">
        <label for="blur">Blur</label><input
          type="range"
          min={0}
          max={5}
          on:change={(e) => {
            blur(e.target.value, selected);
            modifyValue(selected, "blur", applyFilter, selected);
            updateUI(selected, "blur", e.target.value);
          }}
          value={getValue("blur", selected, 0)}
        />
      </div>
      <div class="container">
        <label for="erode">Erode</label><input
          type="range"
          min={0}
          max={5}
          on:change={(e) => {
            erode(e.target.value, selected);
            modifyValue(selected, "erode", applyFilter, selected);
            updateUI(selected, "erode", e.target.value);
          }}
          value={getValue("erode", selected, 0)}
        />
      </div>
      <div class="container">
        <label for="shadow">Shadow</label><input
          type="range"
          min={0}
          max={20}
          on:change={(e) => {
            shadow(e.target.value, selected);
            modifyValue(selected, "shadow", applyFilter, selected);
            updateUI(selected, "shadow", e.target.value);
          }}
          value={getValue("shadow", selected, 0)}
        />
      </div>
      <div class="container">
        <label for="shadow_color">Shadow Color</label><input
          type="color"
          name="shadow_color"
          on:change={(e) => {
            shadowColor(e.target.value, selected);
            modifyValue(selected, "shadow_color", applyFilter, selected);
            updateUI(selected, "shadow_color", e.target.value);
          }}
          value={getValue("shadow_color", selected, "black")}
        />
      </div>

      <div class="container">
        <label for="waves">Waves</label><input
          type="range"
          min={0}
          max={20}
          on:change={(e) => {
            waves(e.target.value, selected);
            modifyValue(selected, "waves", applyFilter, selected);
            updateUI(selected, "waves", e.target.value);
          }}
          value={getValue("waves", selected, 0)}
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
