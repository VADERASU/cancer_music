<script>
  import { API_URL } from "../api/constants";
  import SaveButton from "./SaveButton.svelte";

  export let musicxml;
  const timestamp = new Date().getTime();

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

  async function synthesize() {
    const response = await fetch(`${API_URL}/synthesize`, {
      method: "POST",
      body: musicxml,
    });

    const bytes = await response.arrayBuffer();
    const audio = new Blob([bytes], {
      type: "audio/wav",
    });

    return audio;
  }
</script>

<div class="sticky flex flex-col gap-1 w-max">
  <p>
    Use these buttons to download the mutated piece in a format of your choice.
    If a button has a gray background, you will have to press it twice - once to
    generate the content, and then again to download it.
  </p>
  <div class="sticky flex flex-row gap-1 w-max">
    <SaveButton onClick={playback} filename={`${timestamp}.mid`} text="MIDI" />
    <a href={sheetURL} download={`${timestamp}.musicxml`}>MusicXML</a>
    <SaveButton onClick={synthesize} filename={`${timestamp}.wav`} text="WAV" />
    <slot />
  </div>
</div>
