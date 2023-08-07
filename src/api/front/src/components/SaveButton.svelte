<script>
  // onClick must return a blob
  export let onClick;
  export let text;
  let url;

  async function runClick() {
    const result = await onClick();
    url = window.URL.createObjectURL(result);
  }
</script>

{#if !url}
  <button on:click={() => runClick()}>{text}</button>
{:else}
  <a href={url}>{text}</a>
{/if}

<style>
</style>
