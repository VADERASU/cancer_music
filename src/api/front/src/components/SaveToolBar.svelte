<script>
  import { API_URL } from "../api/constants";

  export let musicxml;

  const sheet = new Blob([musicxml], {
    type: "application/vnd.recordare.musicxml",
  });

  const sheetURL = window.URL.createObjectURL(sheet);

  async function playback() {
    fetch(`${API_URL}/playback`, {
      method: "POST",
      body: musicxml,
    });
  }
</script>

<div class="sticky flex flex-col gap-1 w-max">
  <h2>Download</h2>
  <div class="sticky flex flex-row gap-1 w-max">
    <button on:click={() => playback()}>MIDI</button>
    <a href={sheetURL} download="mutant.musicxml">MusicXML</a>
    <button on:click={() => playback()}>MP3</button>
  </div>
</div>
