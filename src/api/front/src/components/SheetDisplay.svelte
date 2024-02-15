<script>
  import { onMount } from "svelte";
  import {
    blobToNoteSequence,
    Player,
    // StaffSVGVisualizer,
  } from "@magenta/music";

  import { OpenSheetMusicDisplay } from "opensheetmusicdisplay";
  // import { parseMXL } from "../api/parser";

  export let vis;
  export let midi;
  export let musicxml;

  let osmd;
  let midiObject;
  let player;
  let container;
  let playState;
  let time = 0;
  let page = 0;
  // https://magenta.github.io/magenta-js/music/

  onMount(() => {
    osmd = new OpenSheetMusicDisplay(container, {
      drawingParameters: "compacttight",
      followCursor: false,
      disableCursor: false,
      renderSingleHorizontalStaffline: true,
    });
    osmd.load(musicxml).then(() => {
      osmd.render();

      const width = container.offsetWidth;
      const height = container.offsetHeight;
      console.log(vis, container);
      blobToNoteSequence(midi).then((res) => {
        midiObject = res;
        osmd.cursor.show();

        player = new Player(false, {
          run: (note) => {
            // weird edge case where cursor will be thrown off if the rests have different durations
            if (osmd.cursor.NotesUnderCursor().every((e) => e.isRestFlag)) {
              osmd.cursor.next();
            } else if (note.startTime > time) {
              time = note.startTime;
              osmd.cursor.next();
              osmd.cursor.cursorElement.style.top = `0px`;
              osmd.cursor.cursorElement.style.height = `${height}px`;

              const left = parseFloat(
                osmd.cursor.cursorElement.style.left.replace(/[^0-9.]/g, "")
              );
              if (left - container.scrollLeft > width) {
                page += 1;
                container.scrollLeft = page * width;
              }
            }
          },
          stop: () => {
            playState = player.getPlayState();
          },
        });
        osmd.cursor.cursorElement.style.height = `${height}px`;
        osmd.cursor.cursorElement.style.top = `0px`;
        playState = player.getPlayState();
      });
    });
  });

  function resetPlayer() {
    osmd.cursor.reset();
    time = 0;
    page = 0;
    container.scrollLeft = 0;
  }

  function startPlayer() {
    if (playState === "stopped") {
      resetPlayer();
      player.start(midiObject);
    } else if (playState === "started") {
      player.pause();
    } else {
      player.resumeContext();
      player.resume();
    }
    playState = player.getPlayState();
  }
</script>

<div class="w-11/12 mx-auto">
  <div>
    <button on:click={startPlayer}>
      {playState === "started" ? "⏸ " : "▶"}
    </button>
  </div>

  <div class="overflow-scroll max-h-screen">
    <div
      class="overflow-x-scroll overflow-y-hidden z-0"
      bind:this={container}
    />
  </div>
</div>

<style>
</style>
