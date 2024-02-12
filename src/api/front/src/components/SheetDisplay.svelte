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
          // absolute position
          const sx = Math.max(...notePositions);
          if (sx - currentPos > width) {
            // need to scroll!
            currentPos = pages * width;
            pages += 1;

            staves.forEach((s) => {
              // staffOffset = 30
              /* eslint-disable-next-line */
              s.render.parentElement.scrollLeft = currentPos;
            });
          }
        },
        stop: () => {
          // staves.forEach((s) => s.redraw());
        },
      });
      player.start(res);
      console.log(player);
    });
  });
</script>

<div
  class="w-11/12 mx-auto max-h-screen overflow-auto mb-2"
  bind:this={container}
>
  {#each activeInstruments as i}
    <div use:generateStaff={i} />
  {/each}
</div>

<style>
</style>
