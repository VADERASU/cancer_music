<script>
  import { onMount } from "svelte";
  import {
    blobToNoteSequence,
    Player,
    StaffSVGVisualizer,
  } from "@magenta/music";

  export let vis;
  export let midi;
  let activeInstruments = [];
  let midiObject;
  let player;
  let container;
  let playState;
  const staves = [];
  // https://magenta.github.io/magenta-js/music/

  function generateStaff(node, instrument) {
    const staff = new StaffSVGVisualizer(midiObject, node, {
      instruments: [instrument],
      pixelsPerTimeStep: 40,
      scrollType: 2,
    });

    /* eslint-disable-next-line */
    staff.render.parentElement.lastChild.setAttribute("width", staff.width);
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
    console.log(vis, midi);
    const width = container.offsetWidth;
    console.log(container, width);
    blobToNoteSequence(midi).then((res) => {
      activeInstruments = [...new Set(res.notes.map((n) => n.instrument))];
      midiObject = res;
      let currentPos = 0;
      let pages = 1;
      player = new Player(false, {
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
      });
      playState = player.getPlayState();
    });
  });

  function startPlayer() {
    if (playState === "stopped") {
      player.start(midiObject);
      setScrollPosition(0);
    } else if (playState === "started") {
      player.pause();
    } else {
      player.resume();
    }
    playState = player.getPlayState();
  }
</script>

<div
  class="w-11/12 mx-auto max-h-screen overflow-auto mb-2"
  bind:this={container}
>
  <div>
    <button on:click={startPlayer}>
      {playState === "started" ? "⏸ " : "▶"}
    </button>
  </div>
  {#each activeInstruments as i}
    <div use:generateStaff={i} />
  {/each}
</div>

<style>
</style>
