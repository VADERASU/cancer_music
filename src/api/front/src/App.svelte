<script>
  import "./app.css";
  import { Stretch } from "svelte-loading-spinners";
  import * as zip from "@zip.js/zip.js";
  import FilePicker from "./components/FilePicker.svelte";
  import Parameters from "./components/Parameters.svelte";
  import SaveToolBar from "./components/SaveToolBar.svelte";
  import SheetDisplay from "./components/SheetDisplay.svelte";
  import { API_URL } from "./api/constants";

  import analogy from "./images/analogy.svg";
  import original from "./images/original.svg";
  import therapy from "./images/therapy.svg";
  import header from "./images/chaos_music.png";

  let mutant;
  let midi;
  let wav;
  let originalWav;
  let file;
  let fileSheet;
  let mutationMetadata;
  let isLoading = false;
  let hideParams = false;
  let mutationSVG = original;

  function setMutSVG(name) {
    mutationSVG = new URL(`./images/${name}.svg`, import.meta.url).href;
  }

  function resetToDefaults() {
    file = null;
    fileSheet = null;
    mutant = null;
    midi = null;
    originalWav = null;
    wav = null;
    mutationMetadata = null;
    hideParams = false;
  }

  const mouseLeave = () => {
    setMutSVG("original");
  };

  $: if (mutant && mutationMetadata) {
    isLoading = false;
  }

  async function startMutate(params) {
    const fd = new FormData();
    // we need howMany, cancer and therapy mode / start for the vis

    fd.append("file", file, file.name);
    isLoading = true;
    hideParams = true;

    const response = await fetch(
      `${API_URL}/process_file?${new URLSearchParams(params)}`,
      {
        contentType: "multipart/form-data",
        method: "POST",
        body: fd,
      }
    );
    if (!response.ok) {
      const content = await response.json();
      alert(`An error occurred: ${content.message}`);
      hideParams = false;
      isLoading = false;
    } else {
      response
        .blob()
        .then((blob) => {
          const reader = new zip.ZipReader(new zip.BlobReader(blob));
          return reader.getEntries();
        })
        .then((entries) => {
          entries.forEach((e) => {
            if (e.filename.endsWith(".musicxml")) {
              e.getData(new zip.TextWriter()).then((res) => {
                mutant = res;
              });
            }

            if (e.filename.endsWith(".json")) {
              e.getData(new zip.TextWriter()).then((res) => {
                mutationMetadata = params;
                mutationMetadata.tree = JSON.parse(res);
              });
            }

            // check if mutant or original, currently not doing anything with original midi
            // need more foolproof way to check for mutant but this is fine for not
            if (e.filename.endsWith(".mid")) {
              if (e.filename.startsWith("mutant_")) {
                e.getData(new zip.BlobWriter("audio/midi")).then((res) => {
                  midi = res;
                });
              }
            }

            if (e.filename.endsWith(".wav")) {
              if (e.filename.startsWith("mutant_")) {
                e.getData(new zip.BlobWriter("audio/wav")).then((res) => {
                  wav = res;
                });
              } else {
                e.getData(new zip.BlobWriter("audio/wav")).then((res) => {
                  originalWav = res;
                });
              }
            }
          });
        });
    }
  }
</script>

<div class="container mx-auto px-2">
  <div class="gap-2 mx-auto space-y-3">
    <div class="mx-auto gap-2">
      <div class="space-y-2">
        <h1 class="text-4xl text-center">Capturing Cancer with Music</h1>
        <img class="object-cover w-full max-h-96" src={header} alt="header" />
      </div>
      <div class="lg:w-3/4 mx-auto text-pretty space-y-2">
        <p>
          While the science behind cancer is complex, the essence of the disease
          can be elegantly expressed as music. Like musicians in a group,
          working together to produce a piece of music, different cells in our
          body work together to produce a living, breathing person. When cancer
          starts to develop, cells stop doing the work of their organ and start
          replicating out of control. Imagine watching a performance where your
          a few members of your favorite band started repeating themselves
          endlessly and started inviting random people to join them on-stage!
          Eventually, a growing, dissonant, relentless cacophony slowly takes
          over the rest of the performance.
        </p>
        <p>
          We took this analogy and wrote some code that takes sheet music in the
          form of <a href="https://musescore.com/">musicXML</a> files as input and
          returns a "mutated" version of the piece. The code is based on a few simple
          rules, all inspired by the way cancer works on a cellular level.
        </p>
      </div>
    </div>
    <hr />
    <h2 class="mx-auto text-center text-3xl">Background</h2>
    <div class="container space-y-2 lg:flex gap-5">
      <div class="flex-1 space-y-2">
        <h2 class="text-2xl text-center">The Analogy</h2>
        <img class="mx-auto h-48" src={analogy} alt="analogy" />
        <p class="text-pretty">
          We consider each part in a piece as an organ in the body. Each part
          contains measures (cells) and notes (DNA). The code randomly selects
          one or more parts to give cancer to and then starts repeating
          (replicating) a number of measures at a certain point.
        </p>
      </div>

      <div class="flex-1 space-y-2">
        <h2 class="text-2xl text-center">Mutations</h2>
        <img class="mx-auto h-48" src={mutationSVG} alt="original" />
        <p class="text-pretty">
          When a measure is repeated, the notes that make up the measure have a
          chance to be mutated, just like the way DNA changes within mutated
          cells. Each mutation adds dissonance as different cancer parts
          randomly diverge. We defined several types of mutations (hover over
          its name to see how it affects the music):
        </p>
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
        <img src={therapy} alt="therapy" class="h-48 w-48 mx-auto" />
        <p class="text-pretty">
          Most therapies are able to kill the vast majority of cancer cells, but
          often some mutant cells have a mutation that makes them resistant to
          therapy. They survive and replicate, eventually regrowing as a tumor
          of resistant cells. Our program simulates this by silencing only a
          portion of the cancerous parts, leaving others to continue growing.
        </p>
      </div>
    </div>
  </div>
  <div class="gap-2">
    <hr />
    <h2 class="text-3xl text-center">Try it out!</h2>
    {#if !hideParams}
      <FilePicker bind:file bind:fileSheet />
      {#if file !== null}
        <Parameters onSubmit={startMutate} />
      {/if}
    {/if}
    {#if mutant || wav || midi}
      {#key mutant}
        <SaveToolBar
          musicxml={mutant}
          {wav}
          {midi}
          {originalWav}
          filename={file.name.split(".")[0]}
        >
          <button class="red-button" on:click={resetToDefaults}>Reset</button>
        </SaveToolBar>
      {/key}
    {/if}
  </div>
  {#if isLoading}
    <div class="flex justify-center">
      <Stretch color="#000000" />
    </div>
  {/if}
</div>
<div class="min-h-48">
  {#if mutant}
    {#key mutant}
      <SheetDisplay
        musicxml={mutant}
        original={fileSheet}
        mutationParams={mutationMetadata}
      />
    {/key}
  {/if}
</div>
<footer>
  <hr />
  <div class="text-gray-500 text-center">
    <p>
      © Authors 2023-2024 Rostyslav Hnatyshyn, Jiayi Hong, Chris Norby, Ross
      Maciejewski, Carlo Maley
    </p>
  </div>
</footer>

<style lang="postcss">
</style>
