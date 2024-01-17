<script>
  import ProbSlider from "./ProbSlider.svelte";

  export let onSubmit;

  let showAdvancedParams = false;

  let howMany = 4;
  let maxParts = 1;
  let reproductionProbability = 0.1;
  let cancerStart = 0.1;
  let seed = Math.floor(Math.random() * Number.MAX_SAFE_INTEGER);

  const probabilities = {
    noop: 0.05,
    insertion: 0.25,
    transposition: 0.15,
    deletion: 0.15,
    translocation: 0.15,
    inversion: 0.25,
  };

  const therapy = {
    mode: 0, // OFF, CURE
    start: 0.5,
    mutant_survival: 0.5,
  };

  let sum = 1;
  $: sum = Object.values(probabilities)
    .reduce((a, b) => a + b)
    .toFixed(2);

  const submit = () => {
    onSubmit({
      ...probabilities,
      ...therapy,
      how_many: howMany,
      maxParts,
      reproductionProbability,
      seed,
      cancerStart,
    });
  };
</script>

<div>
  <div>
    <input
      id="showParams"
      type="checkbox"
      bind:value={showAdvancedParams}
      bind:checked={showAdvancedParams}
    />
    <label for="showParams">Show advanced options</label>
  </div>
  {#if showAdvancedParams}
    <h2 class="text-2xl">
      Sum of probabilities:
      {#if parseFloat(sum) !== 1.0}
        <span class="text-red-700">
          {Math.round(sum * 100)}%
        </span>
      {:else}
        <span class="text-green-700">
          {Math.round(sum * 100)}%
        </span>
      {/if}
    </h2>
    <div class="flex flex-row gap-3">
      <div class="flex flex-col gap-2">
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
        <div class="flex gap-2">
          <label class="grow" for="how_many"
            >Length of cancer theme: {howMany}</label
          >
          <input
            class="shrink"
            type="range"
            name="how_many"
            min="0"
            max="10"
            bind:value={howMany}
          />
        </div>
        <div class="flex gap-2">
          <label class="grow" for="numberOfParts"
            >Maximum number of mutant parts: {maxParts}</label
          >
          <input
            class="shrink"
            type="range"
            name="numberOfParts"
            min="1"
            max="20"
            bind:value={maxParts}
          />
        </div>
        <ProbSlider text="Reproduction" bind:val={reproductionProbability} />
        <ProbSlider text="Cancer Start" bind:val={cancerStart} />
        <div class="flex gap-2">
          <label class="grow" for="seed">Seed:</label>
          <input class="shrink" type="number" name="seed" bind:value={seed} />
        </div>
      </div>

      <div class="flex flex-col gap-2">
        <div>
          <label for="therapyMode">Therapy type</label>
          <select name="therapyMode" bind:value={therapy.mode}>
            <option value={0}>Off</option>
            <option value={1}>On</option>
          </select>
        </div>
        {#if therapy.mode !== 0}
          <ProbSlider text="Therapy start" bind:val={therapy.start} />
          <ProbSlider
            text="Mutant survival rate"
            bind:val={therapy.mutant_survival}
          />
        {/if}
      </div>
    </div>
  {/if}
  <div class="flex justify-center">
    {#if parseFloat(sum) === 1.0}
      <button class="w-1/2" on:click={submit}>Submit</button>
    {/if}
  </div>
</div>

<style lang="postcss">
</style>
