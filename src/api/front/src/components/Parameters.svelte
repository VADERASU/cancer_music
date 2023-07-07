<script>
  import ProbSlider from "./ProbSlider.svelte";
  import { API_URL } from "../api/constants";

  export let mutant;
  let file;
  let howMany = 4;

  const probabilities = {
    noop: 0.05,
    insertion: 0.25,
    transposition: 0.15,
    deletion: 0.15,
    translocation: 0.15,
    inversion: 0.25,
  };

  const therapy = {
    mode: 0, // OFF, CURED, PARTIAL
    start: 0.5,
    resistance_probability: 0.2,
  };

  let sum = 1;
  $: sum = Object.values(probabilities)
    .reduce((a, b) => a + b)
    .toFixed(2);

  const readFile = (e) => {
    [file] = e.target.files;
  };

  async function readStream(stream) {
    const reader = stream.getReader();

    let bytes = new Uint8Array(0);
    const process = ({ done, value }) => {
      if (done) {
        return;
      }

      // copy old array
      const b = new Uint8Array(bytes.length + value.length);
      b.set(bytes);
      b.set(value, bytes.length);
      bytes = b;

      reader.read().then(process);
    };

    await reader.read().then(process);
    return bytes;
  }

  async function startMutate() {
    const fd = new FormData();
    fd.append("file", file, file.name);
    const response = await fetch(
      `${API_URL}/process_file?${new URLSearchParams({
        ...probabilities,
        ...therapy,
        how_many: howMany,
      })}`,
      {
        contentType: "multipart/form-data",
        method: "POST",
        body: fd,
      }
    );
    readStream(response.body).then((bytes) => {
      mutant = new TextDecoder().decode(bytes);
    });
  }
</script>

<div class="flex flex-col gap-2">
  <input on:change={readFile} type="file" />
  {#if file}
    <h2 class="text-2xl">
      Sum of probabilities:
      {#if parseInt(sum, 10) !== 1.0}
        <span style="color:red">
          {Math.round(sum * 100)}%
        </span>
      {:else}
        <span style="color:green">
          {Math.round(sum * 100)}%
        </span>
      {/if}
    </h2>
    <div class="flex flex-row gap-3">
      <div class="flex flex-col gap-2">
        <div class="flex gap-2">
          <label class="grow" for="how_many">Tumor size: {howMany}</label>
          <input
            class="shrink"
            type="range"
            name="how_many"
            min="0"
            max="10"
            bind:value={howMany}
          />
        </div>
        <ProbSlider text="No mutation" bind:val={probabilities.noop} />
        <ProbSlider text="Insertion" bind:val={probabilities.insertion} />
        <ProbSlider
          text="Transposition"
          bind:val={probabilities.transposition}
        />
        <ProbSlider text="Deletion" bind:val={probabilities.deletion} />
        <ProbSlider
          text="Translocation"
          bind:val={probabilities.translocation}
        />
        <ProbSlider text="Inversion" bind:val={probabilities.inversion} />
      </div>
      <div class="flex flex-col gap-2">
        <div>
          <label for="therapyMode">Therapy type</label>
          <select name="therapyMode" bind:value={therapy.mode}>
            <option value={0}>Off</option>
            <option value={1}>Cure</option>
            <option value={2}>Partial cure</option>
          </select>
        </div>
        {#if therapy.mode !== 0}
          <ProbSlider text="Therapy start" bind:val={therapy.start} />
        {/if}
        {#if therapy.mode === 2}
          <ProbSlider
            text="Mutant survival"
            bind:val={therapy.resistance_probability}
          />
        {/if}
      </div>
    </div>
    {#if parseInt(sum, 10) === 1.0}
      <div>
        <button on:click|preventDefault={startMutate}>Submit</button>
      </div>
    {/if}
  {/if}
</div>

<style lang="postcss">
</style>
