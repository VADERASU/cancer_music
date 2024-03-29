<script>
  import { onMount } from "svelte";
  import { blobToNoteSequence, SoundFontPlayer } from "@magenta/music";

  import { OpenSheetMusicDisplay } from "opensheetmusicdisplay";
  import * as Tone from "tone";

  export let midi;
  export let mutationParams;
  export let musicxml;

  let osmd;
  let midiObject;
  let player;
  let container;
  let playState;
  let time = 0;
  let page = 0;
  // https://magenta.github.io/magenta-js/music/

  function setCursorStyle(h) {
    osmd.cursor.cursorElement.style.height = `${h}px`;
    osmd.cursor.cursorElement.style.top = `0px`;
  }

  onMount(() => {
    osmd = new OpenSheetMusicDisplay(container, {
      drawingParameters: "compacttight",
      followCursor: false,
      disableCursor: false,
      renderSingleHorizontalStaffline: true,
    });

    console.log(mutationParams);

    musicxml.text().then((rawData) => {
      osmd.load(rawData).then(() => {
        osmd.render();

        const width = container.offsetWidth;
        const height = container.offsetHeight;

        // https://dirk.net/2021/10/26/magenta-music-soundfontplayer-instrument-selection/
        blobToNoteSequence(midi).then((res) => {
          midiObject = res;
          osmd.cursor.show();
          setCursorStyle(height);

          player = new SoundFontPlayer(
            "https://storage.googleapis.com/magentadata/js/soundfonts/sgm_plus",
            Tone.Master,
            new Map(),
            new Map(),
            {
              run: (note) => {
                // catch up if we're on rests
                while (
                  osmd.cursor.NotesUnderCursor().every((e) => e.isRestFlag)
                ) {
                  osmd.cursor.next();
                  setCursorStyle(height);
                }
                if (note.startTime > time) {
                  time = note.startTime;
                  osmd.cursor.next();
                  setCursorStyle(height);

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
          playState = player.getPlayState();
        });
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
    setCursorStyle(container.offsetHeight);
    time = 0;
    page = 0;
    container.scrollLeft = 0;
  }

  function startPlayer() {
    // have to set playState manually -- the soundfont player seems to be bugged when setting state
    if (playState === "stopped") {
      resetPlayer();
      player.start(midiObject);
      playState = "started";
    } else if (playState === "started") {
      player.pause();
      playState = player.getPlayState();
    } else {
      player.resumeContext();
      player.resume();
      playState = player.getPlayState();
    }
  }
</script>

<div class="w-11/12 mx-auto">
  {#if player}
    <div>
      <button on:click={startPlayer}>
        {playState === "started" ? "⏸ " : "▶"}
      </button>
    </div>
  {/if}

  <div class="overflow-scroll max-h-screen">
    <div class="overflow-x-scroll overflow-y-clip" bind:this={container} />
  </div>
</div>

<style>
</style>
