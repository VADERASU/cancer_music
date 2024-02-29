<script>
  import { onMount } from "svelte";
  import {
    blobToNoteSequence,
    PianoRollSVGVisualizer,
    SoundFontPlayer,
    NoteSequence,
  } from "@magenta/music";
  // import { OpenSheetMusicDisplay } from "opensheetmusicdisplay";
  import * as Tone from "tone";

  export let midi;
  export let mutationParams;
  export let musicxml;

  let noteGroups = [];
  let midiObject;
  let player;
  let container;
  let playState;
  let currentPos = 0;
  let pages = 1;
  let maxPitch = 0;
  let minPitch = 0;
  const staves = [];

  // https://magenta.github.io/magenta-js/music/

  function generateStaff(node, noteGroup) {
    const staff = new PianoRollSVGVisualizer(noteGroup, node, {
      minPitch,
      maxPitch,
    });

    /* eslint-disable-next-line */
    //staff.render.parentElement.lastChild.setAttribute("width", staff.width);
    console.log(staff);
    staves.push(staff);
  }

  function setScrollPosition(pos) {
    staves.forEach((s) => {
      /* eslint-disable-next-line */
      s.render.parentElement.scrollLeft = pos;
    });
  }

  onMount(() => {
    const width = container.offsetWidth;
    console.log(mutationParams, musicxml);

    // https://dirk.net/2021/10/26/magenta-music-soundfontplayer-instrument-selection/
    blobToNoteSequence(midi).then((res) => {
      midiObject = res;
      const uniqueInstruments = [
        ...new Set(midiObject.notes.map((n) => n.instrument)),
      ];
      const pitches = midiObject.notes.map((n) => n.pitch);
      minPitch = Math.min(...pitches);
      maxPitch = Math.max(...pitches);

      noteGroups = uniqueInstruments.map((id) => {
        const notes = midiObject.notes.filter((n) => n.instrument === id);
        const seq = NoteSequence.decode(
          NoteSequence.encode(midiObject).finish()
        );
        seq.notes = notes;
        return seq;
      });

      player = new SoundFontPlayer(
        "https://storage.googleapis.com/magentadata/js/soundfonts/sgm_plus",
        Tone.Master,
        new Map(),
        new Map(),
        {
          run: (note) => {
            const notePositions = staves.map((s) => s.redraw(note, false));
            const sx = Math.max(...notePositions);
            if (sx - currentPos > width) {
              currentPos = pages * width;
              pages += 1;
              setScrollPosition(currentPos);
            }
          },
          stop: () => {
            playState = player.getPlayState();
          },
        }
      );
      playState = player.getPlayState();
    });

    // cleanup to avoid memory leak
    return () => {
      if (player) {
        player.stop();
      }
    };
  });

  function resetPlayer() {
    pages = 0;
    currentPos = 0;
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

<div class="w-11/12 mx-auto" bind:this={container}>
  {#if player}
    <div>
      <button on:click={startPlayer}>
        {playState === "started" ? "⏸ " : "▶"}
      </button>
    </div>
  {/if}
  {#each noteGroups as ng}
    <svg use:generateStaff={ng} />
  {/each}
</div>

<style>
</style>
