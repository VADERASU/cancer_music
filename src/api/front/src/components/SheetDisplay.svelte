<script>
  import { onMount } from "svelte";
  import * as d3 from "d3";
  import { parseMXL } from "../api/parser";

  export let musicxml;
  export let original;
  export let mutationParams;
  let container;

  const colors = [
    "#a6cee3",
    "#1f78b4",
    "#b2df8a",
    "#33a02c",
    "#fb9a99",
    "#e31a1c",
    "#fdbf6f",
    "#ff7f00",
    "#cab2d6",
    "#6a3d9a",
    "#ffff99",
    "#b15928",
  ];

  const keymap = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
  const accidentalModifier = { n: 0, "#": 1, "##": 2, b: -1, bb: -2, null: 0 };

  onMount(() => {
    const width = container.clientWidth;
    const height = container.clientHeight;
    parseMXL(musicxml).then((sheet) => {
      console.log(original);
      console.log(sheet.Staves);
      console.log(sheet.Parts);
      console.log(mutationParams);
      const measureXScale = d3
        .scaleBand()
        .domain([...Array(sheet.sourceMeasures.length).keys()])
        .range([0, width])
        .paddingInner(0.1);

      const bw = measureXScale.bandwidth();

      // all measures
      d3.select(container)
        .selectAll("svg")
        .data(sheet.sourceMeasures)
        .enter()
        .append("svg")
        .attr("width", bw)
        .attr("height", height)
        .attr("x", (_, i) => measureXScale(i))
        .attr("y", 20)
        .each(function (d) {
          const ml = d.verticalMeasureList;
          const measureYScale = d3
            .scaleBand()
            .domain([...Array(ml.length).keys()])
            .range([0, height])
            .paddingInner(0.1);

          console.log(ml);
          // each vertical measure, corresponding to a part
          d3.select(this)
            .selectAll("svg")
            .data(ml)
            .enter()
            .append("svg")
            .attr("height", measureYScale.bandwidth())
            .attr("width", bw)
            .attr("x", 0)
            .attr("y", (_, i) => measureYScale(i))
            .each(function (m) {
              const voices = Object.values(m.vfVoices).filter(
                (v) =>
                  v.totalTicks.numerator / v.totalTicks.denominator >=
                  v.ticksUsed.numerator / v.ticksUsed.denominator
              );

              const totalLength = Math.max(
                ...voices.map(
                  (v) => v.totalTicks.numerator / v.totalTicks.denominator
                )
              );

              // each measure has 1-N voices
              const voiceHeightScale = d3
                .scaleBand()
                .domain([...Array(voices.length).keys()])
                .range([0, measureYScale.bandwidth()])
                .paddingInner(0.1);

              const vbw = voiceHeightScale.bandwidth();

              d3.select(this)
                .selectAll("svg")
                .data(voices)
                .enter()
                .append("svg")
                .attr("height", vbw)
                .attr("width", bw)
                .attr("x", 0)
                .attr("y", (_, i) => voiceHeightScale(i))
                .each(function (v) {
                  // each voice has 1-N notes
                  const { tickables } = v;
                  const xScale = d3
                    .scaleLinear()
                    .domain([0, totalLength])
                    .range([0, bw]);

                  const notes = tickables.filter(
                    (n) => n.attrs.type !== "GhostNote"
                  );

                  // https://ericjknapp.com/2019/09/26/midi-measures/
                  // shifts pickups correctly
                  let currentTime =
                    totalLength -
                    v.ticksUsed.numerator / v.ticksUsed.denominator;
                  d3.select(this)
                    .selectAll("rect")
                    .data(notes)
                    .enter()
                    .append("rect")
                    .attr("height", vbw)
                    .attr("y", 0)
                    .attr("width", (note) => xScale(note.intrinsicTicks) - 1)
                    .attr("x", (note) => {
                      const time = currentTime;
                      currentTime += note.intrinsicTicks;
                      return xScale(time);
                    })
                    .attr("fill", (note) => {
                      // deal with chords later
                      // don't show rests
                      if (note.noteType === "r") {
                        return "gray";
                      }
                      const keyProp = note.keyProps[0];
                      const { accidental, key } = keyProp;
                      const pitch = key.charAt(0).toUpperCase();

                      let colorIdx =
                        keymap[pitch] + accidentalModifier[accidental];

                      if (colorIdx < 0) {
                        colorIdx += 12;
                      }
                      return colors[colorIdx % colors.length];
                    });
                });
            });
        });
      // sourcemeasures gives you # measures
      // in each sourceMeasure there is activeTimeSignature giving you time
      // vertical measure list gives you each part
      // vf voices is voices per measure
      // tickables.keys & .duration is the note value
    });
  });
</script>

<svg class="w-11/12 mx-auto h-screen" bind:this={container} />

<style>
</style>
