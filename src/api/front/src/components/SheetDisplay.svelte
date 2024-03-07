<script>
  import { onMount } from "svelte";
  import { blobToNoteSequence, SoundFontPlayer } from "@magenta/music";
  import * as Tone from "tone";
  import * as d3 from "d3";
  import { parseMXL } from "../api/parser";

  export let midi;
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
  let svgContainer;
  let pages = 0;
  let currentPos = 0;

  // https://magenta.github.io/magenta-js/music/
  function getAttr(svg, attr) {
    return parseFloat(svg.getAttribute(attr));
  }

  function getGTransform(g) {
    const transform = d3.select(g).attr("transform");
    const raw = transform.replace(/[^0-9.,]/g, "");
    return raw.split(",").map((s) => parseFloat(s));
  }

  function getGx(g) {
    const vals = getGTransform(g);
    return vals[0];
  }

  function setScrollPosition(pos) {
    // staves.forEach((s) => {
    /* eslint-disable-next-line */
    container.scrollLeft = pos;
    // });
  }

  function render(height, sheet) {
    const mutantMeasures = sheet.sourceMeasures;
    const originalParts = Object.keys(mutationParams.tree);
    const measures = [...Array(sheet.sourceMeasures.length).keys()];
    const cancerStart = Math.floor(
      mutationParams.cancerStart * measures.length
    );
    // const therapyStart = Math.floor(mutationParams.start * measures.length) - 1;

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

    const bw = 100;
    const xPad = 5;
    const width = bw * measures.length + (bw * 1.25);

    d3.select(svgContainer).attr("width", width).attr("height", height);

    const partDivisionScale = d3
      .scaleBand()
      .domain(originalParts)
      .range([0, height]);

    const partContainerHeight = partDivisionScale.bandwidth();

    cursorHeight = partContainerHeight * originalParts.length;

    // let therapyStartX = 0;
    // let cancerStartX = 0;
    const notePositions = [];
    d3.select(svgContainer)
      .selectAll("svg")
      .data(originalParts)
      .enter()
      .insert("svg", "rect")
      .attr("width", width)
      .attr("y", (_, i) => i * partContainerHeight)
      .attr("height", partContainerHeight)
      .each(function (partNumber) {
        const childrenParts = mutationParams.tree[partNumber];
        const partAnnotations = mutationParams.annotations[partNumber];

        const getX = (i, w) => {
          if (i > 0) {
            const d = groupedMeasures[i - 1];
            const wl = d.length * bw;
            return getX(i - 1, w + wl + xPad * mutationParams.how_many);
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
                const mML = mutantMeasures[measureNumber].verticalMeasureList;
                ml.push(mML[partNumber]);
                const measureSVG = this;
                const measureAnnotations = partAnnotations
                  ? partAnnotations[measureNumber]
                  : {};
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
                  .attr("height", measureYScale.bandwidth())
                  .attr("width", bw)
                  .attr("x", 0)
                  .attr("y", (_, i) => measureYScale(i))
                  .each(function (m) {
                    if (m) {
                      const voices = Object.values(m.vfVoices);
                      const totalLength = Math.max(
                        ...voices.map(
                          (v) =>
                            v.totalTicks.numerator / v.totalTicks.denominator
                        )
                      );

                      // each measure has 1-N voices
                      const voiceHeightScale = d3
                        .scaleBand()
                        .domain([...Array(voices.length).keys()])
                        .range([0, measureYScale.bandwidth()]);

                      const vbw = voiceHeightScale.bandwidth();

                      const lyrics = measureAnnotations
                        ? Object.values(measureAnnotations)
                        : [];

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
                            .selectAll("g")
                            .data(notes)
                            .enter()
                            .append("g")
                            .attr("transform", (note) => {
                              const t = localTime;
                              localTime += note.intrinsicTicks;
                              return `translate(${xScale(t)}, 0)`;
                            })
                            .each(function (note, i) {
                              // this = the text and rect group
                              let lyric = lyrics[i];

                              if (!lyric) {
                                if (note.noteType === "r") {
                                  lyric = "-";
                                } else {
                                  lyric = "n";
                                }
                              }
                              const noteWidth = xScale(note.intrinsicTicks) - 1;

                              if (lyric) {
                                d3.select(this)
                                  .append("text")
                                  .attr("x", 0)
                                  .attr("y", vbw / 2)
                                  .text(lyric);
                              }

                              if (note.noteType !== "r") {
                                notePositions.push({
                                  svg: this.parentElement,
                                  g: this,
                                  measureNumber,
                                  mgSVG,
                                  measureSVG,
                                  noteWidth,
                                });
                              }
                            });
                        });
                    }
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

    /* if (mutationParams.mode !== 0 && mutationParams.mode !== 3) {
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
      .attr("fill", "red"); */

    // sourcemeasures gives you # measures
    // in each sourceMeasure there is activeTimeSignature giving you time
    // vertical measure list gives you each part
    // vf voices is voices per measure
    // tickables.keys & .duration is the note value
    const sequence = measures.map((measureNumber) => {
      const notes = notePositions.filter(
        (e) => e.measureNumber === measureNumber
      );
      const xGroups = d3.group(notes, (n) => getGx(n.g));
      return [...xGroups.values()]
        .map(
          (g) =>
            g.reduce(
              (acc, v) => {
                const w = v.noteWidth;
                if (w < acc.width) {
                  return { note: v, width: w };
                }
                return acc;
              },
              { note: null, width: Number.MAX_VALUE }
            ).note
        )
        .sort((a, b) => getGx(a.g) - getGx(b.g));
    });
    return sequence.flat();
  }

  function getAbsX(note) {
    return (
      getGx(note.g) + getAttr(note.mgSVG, "x") + getAttr(note.measureSVG, "x")
    );
  }

  function renderCursor() {
    const note = cursorSequence[noteIdx];
    let next = null;
    console.log(note);
    if (noteIdx + 1 < cursorSequence.length) {
      next = cursorSequence[noteIdx + 1];
    }
    if (note) {
      const noteX = getAbsX(note);
      cursor.setAttribute("height", cursorHeight);
      cursor.setAttribute("x", getAbsX(note));
      if (noteX - currentPos > container.clientWidth) {
        currentPos = pages * container.clientWidth;
        pages += 1;
        setScrollPosition(currentPos);
      }
      if (next === null || note.measureSVG !== next.measureSVG) {
        cursor.setAttribute("width", note.noteWidth);
      } else {
        const thisX = getAbsX(note);
        const nextX = getAbsX(next);
        let width = note.noteWidth;
        if (nextX - thisX < width) {
          width = thisX - nextX;
        }
        cursor.setAttribute("width", width);
      }
    }
  }

  onMount(() => {
    musicxml.text().then((rawData) => {
      parseMXL(rawData).then((sheet) => {
        const height = container.clientHeight;

        cursorSequence = render(height, sheet);
        // https://dirk.net/2021/10/26/magenta-music-soundfontplayer-instrument-selection/
        blobToNoteSequence(midi).then((res) => {
          midiObject = res;
          renderCursor();

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
                  renderCursor();
                }
              },
              stop: () => {
                playState = player.getPlayState();
              },
            }
          );
          playState = player.getPlayState();
          // cleanup to avoid memory leak
          return () => {
            if (player) {
              player.stop();
            }
          };
        });
      });
    });
  });
  
  function resetPlayer() {
    time = 0;
    noteIdx = 0;
    pages = 0;
    currentPos = 0;
    renderCursor();
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

  <div class="overflow-auto h-screen" bind:this={container}>
    <svg bind:this={svgContainer}>
      <rect bind:this={cursor} stroke="black" opacity="0.5" stroke-width="3" />
    </svg>
  </div>
</div>

<style>
</style>
