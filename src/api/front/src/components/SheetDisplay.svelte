<script>
  import { onMount } from "svelte";
  import { blobToNoteSequence, SoundFontPlayer } from "@magenta/music";

  import { OpenSheetMusicDisplay } from "opensheetmusicdisplay";
  // import { parseMXL } from "../api/parser";
  import * as Tone from "tone";

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
      console.log(vis, container, osmd);

      // https://dirk.net/2021/10/26/magenta-music-soundfontplayer-instrument-selection/
      blobToNoteSequence(midi).then((res) => {
        midiObject = res;
        console.log(midiObject);
        osmd.cursor.show();

        player = new SoundFontPlayer(
          "https://storage.googleapis.com/magentadata/js/soundfonts/sgm_plus",
          Tone.Master,
          new Map(),
          new Map(),
          {
            run: (note) => {
              // catch up if we're on rests
              while(osmd.cursor.NotesUnderCursor().every((e) => e.isRestFlag)) { 
                osmd.cursor.next();
              }
              if (note.startTime > time) {
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
                } else if (left - container.scrollLeft < 0) {
                  page = 0;
                  container.scrollLeft = 0;
                }
              }
            },
            stop: () => {
              playState = player.getPlayState();
            },
          }
        );
        osmd.cursor.cursorElement.style.height = `${height}px`;
        osmd.cursor.cursorElement.style.top = `0px`;
        playState = player.getPlayState();
      });
    });

    // cleanup to avoid memory leak
    return () => {
      if (player) {
        player.stop();
      }
    };
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
