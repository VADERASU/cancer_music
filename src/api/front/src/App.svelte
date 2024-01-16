<script>
  import "./app.css";
  import Parameters from "./components/Parameters.svelte";
  import SaveToolBar from "./components/SaveToolBar.svelte";
  import SheetDisplay from "./components/SheetDisplay.svelte";

  let mutant;
  let choice = "Canon_in_D.mxl";

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
</script>

<div class="container flex flex-col px-5 gap-2">
  <h1 class="text-3xl">Capturing Cancer with Music</h1>
  <p>
    This is an application for hearing how cancer (and cancer therapy) works.
    While there is an overwhelming complexity in the science and medicine of
    cancer, the essence of the disease can be heard and understood when it is
    translated into music. Here you can upload any piece of music in musicXML
    format. We will simulate the evolution of cancer (and the effects of therapy
    if you want), and give you back an mp3 sound file, a midi file and/or a pdf
    of the sheet music.
  </p>

  <p>
    Our software simulates an analogy between the cell types in a body and the
    parts of a piece of music. Like musicians in a symphony, working together to
    produce a piece of music, different cells in our body work together to
    produce a living, breathing person. In this analogy, cancer starts with a
    musician ceasing to play her assigned part, and starting to repeat her last
    few measures, replicating that motif, generating another part, with some
    probability, every time she repeats. We call that probability of generating
    a new part, the reproductive rate of that part. Cancer cells stop doing the
    work of their organ, and start replicating out of control. As they
    reproduce, they also mutate, and sometimes a mutation gives that cancer cell
    an additional advantage, replicating faster or surviving better than the
    other cells. It is a microcosm of natural selection at the cell level. In
    music, we can hear this as mutations and variations in the cancer motif, and
    in the rate at which the cancer motif replicates itself. A growing,
    dissonant, monotonous and yet relentless cacophony slowly take over the
    symphony.
  </p>

  <p>
    Even the genetic details of the kinds of mutations that occur in cancer can
    be translated into music. Single nucleotide mutations (single letters of the
    DNA) have a natural analogy in single note changes. Small insertions or
    deletions in the DNA can be represented by small repetitions and deletions
    in the motif. Sequences of letters can be reversed in DNA, just as portions
    of the motif could be reversed, and so on. Cancers often fuse part of one
    chromosome to part of another chromosome (called a “translocation”). We can
    model this by taking a part of the cancer motif and fusing it to a randomly
    selected part of some other motif in the original piece. We also allow
    mutations that transpose the cancer motif up or down by one half-step. Each
    mutation adds dissonance as different cancer parts randomly diverge. If a
    mutation changes the reproduction rate of the part, we note this by
    selecting a new timber for the part with the new rate.
  </p>

  <p>
    Cancer therapy can also be represented in music. Most therapies are able to
    kill the vast majority of cancer cells, but it is often the case that some
    mutant cells, by bad luck, have a mutation that makes them resistant to the
    therapy. They survive and replicate, eventually regrowing a tumor that is
    entirely composed of resistant cells. This could be heard in music, as most
    of the cancerous, repeating parts are silenced, but some parts, resistant to
    the therapy, are left behind to replicate again. Because there is often a
    tradeoff between reproduction and survival, we set the chance that a part is
    killed by therapy to be equal to its reproduction rate (signified by the
    timbers).
  </p>

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
{#if mutant}
  {#key mutant}
    <SheetDisplay musicxml={mutant} {vis} />
  {/key}
{/if}

<style lang="postcss">
</style>
