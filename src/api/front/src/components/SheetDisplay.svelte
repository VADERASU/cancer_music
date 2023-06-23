<script>
    import { OpenSheetMusicDisplay } from "opensheetmusicdisplay";
    import { mutationMarkers } from "../api/constants";
    import { initFilters } from "../api/fx";
    import { onMount } from "svelte";

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
        const pages = document
            .getElementById("sheet")
            .getElementsByTagName("svg");
        for (const svg of pages) {
            const defs = svg.getElementsByTagName("defs");
            if (defs.length === 0) {
                initFilters(svg);
            }
        }
        for (const mutation of Object.keys(vis)) {
            const marker = mutationMarkers[mutation];
            const fx = vis[mutation];
            for (const m of osmd.graphic.measureList) {
                const mutantMeasure = m[m.length - 1];
                for (const s of mutantMeasure.staffEntries) {
                    for (const lyric of s.lyricsEntries) {
                        if (lyric.lyricsEntry.text === marker) {
                            for (const effect of Object.values(fx)) {
                                effect(s);
                            }
                        }
                    }
                }
            }
        }
    }
</script>

<div id="sheet" bind:this={container} />

<style>
</style>
