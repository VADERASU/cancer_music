<script>
    import ProbSlider from "./ProbSlider.svelte";
    import { API_URL } from "../api/constants.js";
    export let mutant;
    let file;
    let how_many = 4;

    let probabilities = {
        noop: 0.05,
        insertion: 0.25,
        transposition: 0.15,
        deletion: 0.15,
        translocation: 0.15,
        inversion: 0.25,
    };

    let therapy = {
        mode: 0, //OFF, CURED, PARTIAL
        start: 0.5,
        resistance_probability: 0.2,
    };

    let sum = 1.0;
    $: sum = Object.values(probabilities)
        .reduce((a, b) => a + b)
        .toFixed(2);

    const readFile = (e) => {
        file = e.target.files[0];
    };

    async function readStream(stream) {
        const reader = stream.getReader();

        let bytes = new Uint8Array(0);
        const process = ({ done, value }) => {
            if (done) {
                return;
            }

            // copy old array
            const b = new Uint8Array(bytes.length + value.length);
            b.set(bytes);
            b.set(value, bytes.length);
            bytes = b;

            return reader.read().then(process);
        };

        await reader.read().then(process);
        return bytes;
    }

    async function startMutate() {
        const fd = new FormData();
        fd.append("file", file, file.name);
        const response = await fetch(
            `${API_URL}/process_file?` +
                new URLSearchParams({
                    ...probabilities,
                    ...therapy,
                    how_many,
                }),
            {
                contentType: "multipart/form-data",
                method: "POST",
                body: fd,
            }
        );
        readStream(response.body).then((bytes) => {
            mutant = new TextDecoder().decode(bytes);
        });
    }
</script>

<div>
    <input on:change={readFile} type="file" />
    {#if file}
        <h2>
            Sum of probabilities:
            {#if sum != 1.0}
                <span style="color:red">
                    {Math.round(sum * 100)}%
                </span>
            {:else}
                <span style="color:green">
                    {Math.round(sum * 100)}%
                </span>
            {/if}
        </h2>
        <form>
            <div>
                <label for="how_many">Tumor size: {how_many}</label>
                <input
                    type="range"
                    name="how_many"
                    min="0"
                    max="10"
                    bind:value={how_many}
                />
            </div>
            <ProbSlider text="No mutation" bind:val={probabilities.noop} />
            <ProbSlider text="Insertion" bind:val={probabilities.insertion} />
            <ProbSlider
                text="Transposition"
                bind:val={probabilities.transposition}
            />
            <ProbSlider text="Deletion" bind:val={probabilities.deletion} />
            <ProbSlider
                text="Translocation"
                bind:val={probabilities.translocation}
            />
            <ProbSlider text="Inversion" bind:val={probabilities.inversion} />
            <h2>Therapy</h2>
            <div>
                <label for="therapyMode">Therapy type</label>
                <select name="therapyMode" bind:value={therapy.mode}>
                    <option value={0}>Off</option>
                    <option value={1}>Cure</option>
                    <option value={2}>Partial cure</option>
                </select>
            </div>
            {#if therapy.mode !== 0}
                <ProbSlider text="Therapy start" bind:val={therapy.start} />
            {/if}
            {#if therapy.mode === 2}
                <ProbSlider
                    text="mutant resistance"
                    bind:val={therapy.resistance_probability}
                />
            {/if}
        </form>
        {#if sum == 1.0}
            <br />
            <button on:click={startMutate}>Submit</button>
        {/if}
    {/if}
</div>

<style>
    form > div {
        display: flex;
        justify-content: space-between;
    }
</style>
