<script>
  import { parseMXL, mxlToString } from "../api/parser";

  export let file;
  export let fileSheet;

  let choice = "twinkle.mxl";

  async function loadMXL(fname) {
    if (fname.includes(".mxl")) {
      const url = new URL(`../samples/${choice}`, import.meta.url).href;
      const md = {
        type: "application/vnd.recordare.musicxml",
      };

      const f = await fetch(url)
        .then((res) => res.blob())
        .then((blob) => new File([blob], choice, md));
      return f;
    }
    return null;
  }

  $: loadMXL(choice).then((res) => {
    file = res;
  });

  const readFile = (e) => {
    [file] = e.target.files;
  };

  $: if (file) {
    mxlToString(file)
      .then((text) => parseMXL(text))
      .then((content) => {
        fileSheet = content;
      });
  }
</script>

<div>
  <p>
    <b>Select a song to mutate or choose your own. </b>
  </p>
  <div>
    <select bind:value={choice} name="file_choice">
      <option value="twinkle.mxl">Twinkle Twinkle Little Star</option>
      <option value="Canon_in_D.mxl">Canon in D</option>
      <option value="Frere_Jacques_Flute_Round.mxl">Frere Jacques</option>
      <option value="Happy_Birthday_To_You_Piano.mxl">Happy Birthday</option>
      <option value="Mary_Had_A_Little_Lamb_Beginner_Piano.mxl"
        >Mary Had a Little Lamb</option
      >
      <option value="user_selected">Choose your own file</option>
    </select>

    {#if choice === "user_selected"}
      <input on:change={readFile} type="file" accept=".mxl,.musicxml" />
      {#if file === null}
        <p class="text-gray-400">
          <em>Note: The file must have a .mxl or .musicxml extension.</em>
        </p>
      {/if}
    {/if}
  </div>
</div>
