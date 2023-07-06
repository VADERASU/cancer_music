<script>
  import { OpenSheetMusicDisplay } from "opensheetmusicdisplay";
  import { onMount } from "svelte";
  import { mutationMarkers } from "../api/constants";

  export let vis;
  export let musicxml;
  let container;
  let osmd;

  onMount(() => {
    osmd = new OpenSheetMusicDisplay(container);
    osmd.load(musicxml).then(() => {
      osmd.render();
    });
  });

  $: if (osmd) {
    Object.keys(vis).forEach((mutation) => {
      const marker = mutationMarkers[mutation];
      const fx = vis[mutation];
      osmd.graphic.measureList.forEach((m) => {
        m.forEach((part) => {
          if (part.parentStaff.parentInstrument.idString.includes("mutant")) {
            part.staffEntries.forEach((s) => {
              s.lyricsEntries.forEach((lyric) => {
                if (lyric.lyricsEntry.text === marker) {
                  Object.values(fx).forEach((effect) => effect(s));
                }
              });
            });
          }
        });
      });
    });
  }
</script>

<div class="w-full" id="sheet" bind:this={container} />

<style>
</style>
