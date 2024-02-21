<script>
  import ProbSlider from "./ProbSlider.svelte";

  export let onSubmit;

  let showAdvancedParams = false;

  let howMany = 4;
  let maxParts = 4;
  let reproductionProbability = 0.3;
  let cancerStart = 0.25;
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
    mode: 2, // OFF, CURE
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
      midi: true,
      wav: true,
    });
  };
</script>

<div class="space-y-2">
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
    <p>
      <b> Sum of probabilities: </b>
      {#if parseFloat(sum) !== 1.0}
        <span class="text-red-700">
          {Math.round(sum * 100)}%
        </span>
      {:else}
        <span class="text-green-700">
          {Math.round(sum * 100)}%
        </span>
      {/if}
    </p>
    <div class="space-y-3 lg:space-y-0 lg:flex lg:flex-row gap-3">
      <hr class="lg:hidden" />
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
      <hr class="lg:hidden" />

      <div class="flex flex-col gap-2">
        <div class="flex gap-2">
          <label class="grow" for="how_many"
            >Length of cancer theme: <b>{howMany}</b></label
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
            >Maximum number of mutant parts: <b>{maxParts}</b></label
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
      <hr class="lg:hidden" />
      <div class="flex flex-col gap-2">
        <div class="flex gap-2">
          <label class="grow" for="therapyMode">Therapy</label>
          <select name="therapyMode" bind:value={therapy.mode}>
            <option value={0}>Off</option>
            <option value={1}>Full Cure</option>
            <option value={2}>Partial Cure</option>
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
      <button class="" on:click={submit}>Mutate</button>
    {/if}
  </div>
</div>

<style lang="postcss">
</style>
