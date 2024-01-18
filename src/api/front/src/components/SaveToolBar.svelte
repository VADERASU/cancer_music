<script>
  import { Stretch } from "svelte-loading-spinners";

  export let musicxml;
  export let midi;
  export let wav;

  const timestamp = new Date().getTime();

  const sheet = new Blob([musicxml], {
    type: "application/vnd.recordare.musicxml",
  });

  let sheetURL;
  $: sheetURL = sheet ? window.URL.createObjectURL(sheet) : null;

  let midiURL;
  $: midiURL = midi ? window.URL.createObjectURL(midi) : null;

  let wavURL;
  $: wavURL = wav ? window.URL.createObjectURL(wav) : null;
</script>

<div class="sticky flex flex-col gap-1 w-max">
  <p>
  Download as...
  </p>
  <div>
    {#if midiURL}
      <a href={midiURL} download={`${timestamp}.mid`}>MIDI</a>
    {:else}
      <Stretch color="#000000" size="20" />
    {/if}
    {#if sheetURL}
      <a href={sheetURL} download={`${timestamp}.mxl`}>MusicXML</a>
    {/if}
    {#if wavURL}
      <a href={wavURL} download={`${timestamp}.wav`}>WAV</a>
    {:else}
      <Stretch color="#000000" size="20"/>
    {/if}
    <slot />
  </div>
</div>
