<script>
  import "./app.css";
  import Parameters from "./components/Parameters.svelte";
  import SaveToolBar from "./components/SaveToolBar.svelte";
  import SheetDisplay from "./components/SheetDisplay.svelte";
  import analogy from "./images/analogy.svg";
  import original from "./images/original.svg";
  import therapy from "./images/therapy.svg";

  let mutant;
  let choice = "Canon_in_D.mxl";

  let mutationSVG = original;

  function setMutSVG(name) {
    mutationSVG = new URL(`./images/${name}.svg`, import.meta.url).href;
  }

  async function loadMXL(fname) {
    if (fname.includes(".mxl")) {
      const url = new URL(`./samples/${choice}`, import.meta.url).href;
      const md = {
        type: "application/vnd.recordare.musicxml",
      };

      const f = await fetch(url)
        .then((res) => res.blob())
        .then((blob) => new File([blob], choice, md));
      return f;
    }
    return null;
  }

  let file;
  $: loadMXL(choice).then((res) => {
    file = res;
  });

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
      cure: {},
    };
    showParams = false;
  }

  const readFile = (e) => {
    [file] = e.target.files;
  };

  const mouseLeave = () => {
    setMutSVG("original");
  };
</script>

<div class="container gap-2 mx-auto">
  <div class="h-screen gap-2 mx-auto space-y-5">
    <div class="w-1/2 mx-auto space-y-2">
      <h1 class="text-3xl text-center">Capturing Cancer with Music</h1>
      <p>
        While the science and treatment of cancer is complex, the essence of the
        disease can be elegantly expressed as music. Like musicians in a group,
        working together to produce a piece of music, different cells in our
        body work together to produce a living, breathing person. When cancer
        starts to develop, cells stop doing the work of their organ and start
        replicating out of control. Imagine watching a performance where your a
        few members of your favorite band started repeating themselves endlessly
        and started inviting random people to join them on-stage! Eventually, a
        growing, dissonant, relentless cacophony slowly takes over the rest of
        the performance.
      </p>
      <p>
        We took this analogy and wrote some code that takes sheet music in the
        form of musicXML files as input and returns a "mutated" version of the
        piece. The code is based on a few simple rules, all inspired by the way
        cancer works on a cellular level.
      </p>
    </div>
    <div class="container flex gap-5">
      <div class="flex-1 space-y-2">
        <h2 class="text-2xl text-center">The Analogy</h2>
        <img class="mx-auto h-48" src={analogy} alt="analogy" />
        <p>
          We consider each part in a piece as an organ in the body. Each part
          contains measures (cells) and notes (DNA). The code randomly selects
          one or more parts to give cancer to and then starts repeating
          (replicating) a number of measures at a certain point.
        </p>
      </div>

      <div class="flex-1 space-y-2">
        <h2 class="text-2xl text-center">Mutations</h2>
        <img class="mx-auto h-48" src={mutationSVG} alt="original" />
        When a measure is repeated, the notes that make up the measure have a chance
        to be mutated, just like the way DNA changes within mutated cells. Each mutation
        adds dissonance as different cancer parts randomly diverge. We defined several
        types of mutations (hover over its name to see how it affects the music):

        <ul class="list-disc list-inside">
          <li>
            <span
              class="mutationSpan"
              on:mouseenter={() => setMutSVG("insertion")}
              on:mouseleave={mouseLeave}>Insertion</span
            > - a sequence of notes repeat.
          </li>
          <li>
            <span
              class="mutationSpan"
              on:mouseenter={() => setMutSVG("deletion")}
              on:mouseleave={mouseLeave}>Deletion</span
            > - a sequence of notes are removed.
          </li>
          <li>
            <span
              class="mutationSpan"
              on:mouseenter={() => setMutSVG("inversion")}
              on:mouseleave={mouseLeave}>Inversion</span
            >- a sequence of notes are reversed.
          </li>
          <li>
            <span
              class="mutationSpan"
              on:mouseenter={() => setMutSVG("translocation")}
              on:mouseleave={mouseLeave}>Translocation</span
            > - the entire measure is replaced by another.
          </li>
          <li>
            <span
              class="mutationSpan"
              on:mouseenter={() => setMutSVG("transposition")}
              on:mouseleave={mouseLeave}>Transposition</span
            > - a single note's pitch changes.
          </li>
        </ul>
      </div>

      <div class="flex-1 space-y-2">
        <h2 class="text-2xl text-center">Therapy</h2>
        <img src={therapy} alt="therapy" class="h-48 mx-auto" />
        <p>
          There is an option to simulate chemotherapy on the piece. Most
          therapies are able to kill the vast majority of cancer cells, but
          often some mutant cells have a mutation that makes them resistant to
          therapy. They survive and replicate, eventually regrowing as a tumor
          of resistant cells. This can be heard in the music, as most of the
          cancerous, repeating parts are silenced, but some parts, resistant to
          the therapy, are left behind to replicate again.
        </p>
      </div>
    </div>
  </div>
  <hr />
  <div class="h-screen">
    <p>Select a song to mutate or choose your own.</p>
    <input
      bind:group={choice}
      type="radio"
      id="choice1"
      name="file_choice"
      value="Canon_in_D.mxl"
    />
    <label for="choice1">Canon in D</label>
    <input
      bind:group={choice}
      type="radio"
      id="choice2"
      name="file_choice"
      value="Frere_Jacques_Flute_Round.mxl"
    />
    <label for="choice2">Frere Jacques</label>
    <input
      bind:group={choice}
      type="radio"
      id="choice3"
      name="file_choice"
      value="Happy_Birthday_To_You_Piano.mxl"
    />
    <label for="choice3">Happy Birthday</label>
    <input
      bind:group={choice}
      type="radio"
      id="choice4"
      name="file_choice"
      value="Mary_Had_A_Little_Lamb_Beginner_Piano.mxl"
    />
    <label for="choice4">Mary Had a Little Lamb</label>
    <input
      bind:group={choice}
      type="radio"
      id="choice5"
      name="file_choice"
      value="user_selected"
    />
    <label for="choice5">Choose your own file</label>
    {#if choice === "user_selected"}
      <input on:change={readFile} type="file" />
    {/if}

    {#if showParams}
      <Parameters bind:mutant bind:file />
    {/if}
    {#if mutant}
      {#key mutant}
        <SaveToolBar musicxml={mutant} />
      {/key}
    {/if}
  </div>
</div>
{#if mutant}
  {#key mutant}
    <SheetDisplay musicxml={mutant} {vis} />
  {/key}
{/if}

<style lang="postcss">
</style>
