<script>
  import { API_URL } from "../api/constants";
  import SaveButton from "./SaveButton.svelte";

  export let musicxml;

  const sheet = new Blob([musicxml], {
    type: "application/vnd.recordare.musicxml",
  });

  const sheetURL = window.URL.createObjectURL(sheet);

  async function playback() {
    const response = await fetch(`${API_URL}/playback`, {
      method: "POST",
      body: musicxml,
    });
    const bytes = await response.arrayBuffer();
    const midi = new Blob([bytes], {
      type: "audio/midi",
    });
    return midi;
  }
</script>

<div class="sticky flex flex-col gap-1 w-max">
  <h2>Download</h2>
  <div class="sticky flex flex-row gap-1 w-max">
    <SaveButton onClick={playback} text="MIDI" />
    <a href={sheetURL} download="mutant.musicxml">MusicXML</a>
    <button on:click={() => playback()}>MP3</button>
  </div>
</div>
