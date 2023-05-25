<script>
    import { OpenSheetMusicDisplay } from "opensheetmusicdisplay";
    export let musicxml;
    let container;

    $: {
        if (container) {
            let osmd = new OpenSheetMusicDisplay(container);
            osmd.load(musicxml).then(() => osmd.render());
        }
    }
</script>

<div id="sheet" bind:this={container} />

<style>
</style>
