<script>
  import { onMount } from "svelte";
  import { blobToNoteSequence, SoundFontPlayer } from "@magenta/music";

  import * as Tone from "tone";
  import * as d3 from "d3";
  import { parseMXL } from "../api/parser";

  export let midi;
  export let original;
  export let mutationParams;
  export let musicxml;

  let midiObject;
  let player;
  let cursor;
  let container;
  let playState;
  let time = 0;
  let noteIdx = 0;
  let cursorSequence = [];
  let cursorHeight = 0;

  // https://magenta.github.io/magenta-js/music/

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

  function getAttr(svg, attr) {
    return parseFloat(svg.getAttribute(attr));
  }

  function render(width, height, sheet) {
    const ogMeasures = original.sourceMeasures;
    const mutantMeasures = sheet.sourceMeasures;
    const originalParts = Object.keys(mutationParams.tree);
    const measures = [...Array(sheet.sourceMeasures.length).keys()];
    const cancerStart = Math.floor(
      mutationParams.cancerStart * measures.length
    );
    const therapyStart = Math.floor(mutationParams.start * measures.length);
    const howMany = mutationParams.how_many;
    const groupedMeasures = [];
    groupedMeasures.push(measures.slice(0, cancerStart));
    for (let i = cancerStart; i < measures.length; i += howMany) {
      if (i < measures.length - howMany) {
        groupedMeasures.push(measures.slice(i, i + howMany));
      } else {
        groupedMeasures.push(measures.slice(i, measures.length));
      }
    }

    const measureXScale = d3
      .scaleBand()
      .domain(measures)
      .range([0, width])
      .paddingInner(0.1);

    const measureXScaleUnPadded = d3
      .scaleBand()
      .domain(measures)
      .range([0, width]);

    const xPad = measureXScaleUnPadded.bandwidth() - measureXScale.bandwidth();

    const bw = measureXScale.bandwidth();

    const partDivisionScale = d3
      .scaleBand()
      .domain(originalParts)
      .range([0, height])
      .paddingInner(0.1);

    const partContainerHeight = partDivisionScale.bandwidth();

    cursorHeight = partContainerHeight * originalParts.length;

    let therapyStartX = 0;
    let cancerStartX = 0;
    const notePositions = [];
    d3.select(container)
      .selectAll("svg")
      .data(originalParts)
      .enter()
      .insert("svg", "rect")
      .attr("width", width)
      .attr("y", (_, i) => i * partContainerHeight)
      .attr("height", partContainerHeight)
      .each(function (partNumber) {
        const ogStop = Math.floor(
          mutationParams.cancerStart * measures.length + mutationParams.how_many
        );

        const childrenParts = mutationParams.tree[partNumber];

        const getX = (i, w) => {
          if (i > 0) {
            const d = groupedMeasures[i - 1];
            const wl = d.length * bw;
            return getX(i - 1, w + wl + (xPad * mutationParams.how_many));
          }
          return w;
        };

        d3.select(this)
          .selectAll("svg")
          .data(groupedMeasures)
          .enter()
          .append("svg")
          .attr("x", (_, i) => getX(i, 0))
          .attr("width", (d) => d.length * bw)
          .attr("height", partContainerHeight)
          .each(function (measureGroup) {
            d3.select(this)
              .append("rect")
              .attr("stroke", "lightgray")
              .attr("stroke-width", 3)
              .attr("width", measureGroup.length * bw)
              .attr("height", partContainerHeight)
              .attr("fill", "none");

            const mgSVG = this;
            d3.select(this)
              .selectAll("svg")
              .data(measureGroup)
              .enter()
              .append("svg")
              .attr("x", (_, i) => i * bw)
              .attr("width", bw)
              .attr("height", partContainerHeight)
              .each(function (measureNumber) {
                const ml = [];
                const ogML = ogMeasures[measureNumber].verticalMeasureList;
                const mML = mutantMeasures[measureNumber].verticalMeasureList;
                if (measureNumber < ogStop) {
                  ml.push(ogML[partNumber]);
                } else {
                  ml.push(mML[partNumber]);
                }
                const measureSVG = this;

                if (measureNumber === therapyStart) {
                  therapyStartX =
                    getAttr(mgSVG, "x") + getAttr(measureSVG, "x");
                }

                if (measureNumber === cancerStart) {
                  cancerStartX = getAttr(mgSVG, "x") + getAttr(measureSVG, "x");
                }

                childrenParts.forEach((pn) => ml.push(mML[pn]));

                const measureYScale = d3
                  .scaleBand()
                  .domain([...Array(ml.length).keys()])
                  .range([0, partContainerHeight])
                  .paddingInner(0.05);

                // each vertical measure, corresponding to a part
                d3.select(this)
                  .selectAll("svg")
                  .data(ml)
                  .enter()
                  .append("svg")
                  .attr("opacity", (_, i) => {
                    if (
                      i === 0 &&
                      measureNumber >=
                        Math.floor(
                          mutationParams.cancerStart * measures.length
                        ) &&
                      childrenParts.length > 0 &&
                      Math.floor(mutationParams.cancerStart * measures.length) +
                        mutationParams.how_many -
                        1 >=
                        measureNumber
                    ) {
                      return 0.3;
                    }
                    return 1.0;
                  })
                  .attr("height", measureYScale.bandwidth())
                  .attr("width", bw)
                  .attr("x", 0)
                  .attr("y", (_, i) => measureYScale(i))
                  .each(function (m) {
                    const voices = Object.values(m.vfVoices);

                    const totalLength = Math.max(
                      ...voices.map(
                        (v) => v.totalTicks.numerator / v.totalTicks.denominator
                      )
                    );

                    // each measure has 1-N voices
                    const voiceHeightScale = d3
                      .scaleBand()
                      .domain([...Array(voices.length).keys()])
                      .range([0, measureYScale.bandwidth()]);

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
                        let localTime = 0;
                        // totalLength -
                        // v.ticksUsed.numerator / v.ticksUsed.denominator;

                        d3.select(this)
                          .selectAll("rect")
                          .data(notes)
                          .enter()
                          .append("rect")
                          .attr("height", vbw)
                          .attr("y", 0)
                          .attr(
                            "width",
                            (note) => xScale(note.intrinsicTicks) - 1
                          )
                          .attr("x", (note) => {
                            const t = localTime;
                            localTime += note.intrinsicTicks;
                            return xScale(t);
                          })
                          .attr("fill", (note) => {
                            // deal with chords later
                            // don't show rests
                            if (note.noteType === "r") {
                              return "#DADADA";
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
                          })
                          .each(function (note) {
                            if (note.noteType !== "r") {
                              notePositions.push({
                                svg: this,
                                measureNumber,
                                mgSVG,
                                measureSVG,
                              });
                            }
                          });
                      });
                  });
                if (
                  measureGroup.indexOf(measureNumber) !==
                  measureGroup.length - 1
                ) {
                  d3.select(this)
                    .append("rect")
                    .attr("width", 1)
                    .attr("x", bw)
                    .attr("height", partContainerHeight)
                    .attr("fill", "none")
                    .attr("stroke-width", 3)
                    .attr("stroke", "black");
                }
              });
          });
      });

    if (mutationParams.mode !== 0) {
      d3.select(container)
        .append("rect")
        .attr("x", therapyStartX)
        .attr("height", cursorHeight)
        .attr("width", 5)
        .attr("fill", "blue");
    }

    d3.select(container)
      .append("rect")
      .attr("x", cancerStartX)
      .attr("height", cursorHeight)
      .attr("width", 5)
      .attr("fill", "red");

    // sourcemeasures gives you # measures
    // in each sourceMeasure there is activeTimeSignature giving you time
    // vertical measure list gives you each part
    // vf voices is voices per measure
    // tickables.keys & .duration is the note value
    const sequence = measures.map((measureNumber) => {
      const notes = notePositions.filter(
        (e) => e.measureNumber === measureNumber
      );
      const xGroups = d3.group(notes, (n) => getAttr(n.svg, "x"));
      return [...xGroups.values()]
        .map(
          (g) =>
            g.reduce(
              (acc, v) => {
                const w = getAttr(v.svg, "width");
                if (w < acc.width) {
                  return { note: v, width: w };
                }
                return acc;
              },
              { note: null, width: Number.MAX_VALUE }
            ).note
        )
        .sort((a, b) => getAttr(a.svg, "x") - getAttr(b.svg, "x"));
    });
    return sequence.flat();
  }

  function renderCursor(note) {
    if (note) {
      cursor.setAttribute("height", cursorHeight);
      cursor.setAttribute("width", getAttr(note.svg, "width"));
      cursor.setAttribute(
        "x",
        getAttr(note.svg, "x") +
          getAttr(note.mgSVG, "x") +
          getAttr(note.measureSVG, "x")
      );
    }
  }

  onMount(() => {
    parseMXL(musicxml).then((sheet) => {
      const width = container.clientWidth;
      const height = container.clientHeight;

      cursorSequence = render(width, height, sheet);
      // https://dirk.net/2021/10/26/magenta-music-soundfontplayer-instrument-selection/
      blobToNoteSequence(midi).then((res) => {
        midiObject = res;
        renderCursor(cursorSequence[0]);

        player = new SoundFontPlayer(
          "https://storage.googleapis.com/magentadata/js/soundfonts/sgm_plus",
          Tone.Master,
          new Map(),
          new Map(),
          {
            run: (note) => {
              if (note.startTime > time) {
                time = note.startTime;
                noteIdx += 1;
                renderCursor(cursorSequence[noteIdx]);
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

    // cleanup to avoid memory leak
    return () => {
      if (player) {
        player.stop();
      }
    };
  });

  function resetPlayer() {
    time = 0;
    noteIdx = 0;
    renderCursor(cursorSequence[noteIdx]);
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

  <svg class="w-full h-screen" bind:this={container}>
    <rect bind:this={cursor} stroke="black" opacity="0.5" stroke-width="3" />
  </svg>
</div>

<style>
</style>
