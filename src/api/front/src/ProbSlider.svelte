<script>
    export let text;
    export let val;
</script>

<div>
    <label for="slider"> Probability of {text}: {Math.round(val * 100)}%</label>
    <input
        type="range"
        name="slider"
        min="0"
        max="1"
        step="0.05"
        bind:value={val}
    />
</div>

<style>
    div {
        display: flex;
        justify-content: space-between;
    }
</style>
