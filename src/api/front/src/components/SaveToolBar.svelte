<script>
  export let musicxml;
  export let midi;
  export let wav;

  const timestamp = new Date().getTime();

  const sheet = new Blob([musicxml], {
    type: "application/vnd.recordare.musicxml",
  });

  const sheetURL = window.URL.createObjectURL(sheet);
  const midiURL = window.URL.createObjectURL(midi);
  const wavURL = window.URL.createObjectURL(wav);

</script>

<div class="sticky flex flex-col gap-1 w-max">
  <p>
    Use these buttons to download the mutated piece in a format of your choice.
  </p>
  <div class="sticky flex flex-row gap-1 w-max">
    <a href={midiURL} download={`${timestamp}.mid`}>MIDI</a>
    <a href={sheetURL} download={`${timestamp}.mxl`}>MusicXML</a>
    <a href={wavURL} download={`${timestamp}.wav`}>WAV</a>
    <slot />
  </div>
</div>
