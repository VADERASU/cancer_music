<script>
  import { Stretch } from "svelte-loading-spinners";

  export let musicxml;
  export let midi;
  export let wav;
  export let filename;
  export let originalWav;

  const sheet = new Blob([musicxml], {
    type: "application/vnd.recordare.musicxml+xml",
  });

  let sheetURL;
  $: sheetURL = sheet ? window.URL.createObjectURL(sheet) : null;

  let midiURL;
  $: midiURL = midi ? window.URL.createObjectURL(midi) : null;

  let wavURL;
  $: wavURL = wav ? window.URL.createObjectURL(wav) : null;

  let originalWavURL;
  $: originalWavURL = originalWav ? window.URL.createObjectURL(originalWav) : null;
</script>

<div class="sticky flex flex-col gap-1 w-full mb-2">
  <div class="flex-1">
    <p>Download as...</p>
    {#if midiURL}
      <a href={midiURL} class="link-button" download={`mutant_${filename}.mid`}
        >MIDI</a
      >
    {:else}
      <Stretch color="#000000" size="20" />
    {/if}
    {#if sheetURL}
      <a
        href={sheetURL}
        class="link-button"
        download={`mutant_${filename}.musicxml`}>MusicXML</a
      >
    {/if}
    {#if wavURL}
      <a href={wavURL} class="link-button" download={`mutant_${filename}.wav`}
        >WAV</a
      >
    {:else}
      <Stretch color="#000000" size="20" />
    {/if}
    <slot />
  </div>

  {#if originalWavURL}
    <div class="w-full justify-center">
      Original
      <audio class="mx-auto w-full" controls>
        <source src={originalWavURL} type="audio/wav" />
        Your browser does not support the audio element.
      </audio>
    </div>
  {/if}

  {#if wavURL}
    <div class="w-full justify-center">
      Mutated

      <audio class="mx-auto w-full" controls>
        <source src={wavURL} type="audio/wav" />
        Your browser does not support the audio element.
      </audio>
    </div>
  {/if}
</div>
