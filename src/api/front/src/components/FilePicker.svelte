<script>
  export let file;

  let choice = "Canon_in_D.mxl";

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
</script>

<div >
  <p>
    <b>Select a song to mutate or choose your own. </b>
  </p>
  <p><em>Note: The file must have a .mxl extension.</em></p>
  <div>
    <div>
      <input
        bind:group={choice}
        type="radio"
        id="choice1"
        name="file_choice"
        value="Canon_in_D.mxl"
      />
      <label for="choice1">Canon in D</label>
    </div>
    <div>
      <input
        bind:group={choice}
        type="radio"
        id="choice2"
        name="file_choice"
        value="Frere_Jacques_Flute_Round.mxl"
      />
      <label for="choice2">Frere Jacques</label>
    </div>
    <div>
      <input
        bind:group={choice}
        type="radio"
        id="choice3"
        name="file_choice"
        value="Happy_Birthday_To_You_Piano.mxl"
      />
      <label for="choice3">Happy Birthday</label>
    </div>
    <div>
      <input
        bind:group={choice}
        type="radio"
        id="choice4"
        name="file_choice"
        value="Mary_Had_A_Little_Lamb_Beginner_Piano.mxl"
      />
      <label for="choice4">Mary Had a Little Lamb</label>
    </div>
    <div>
      <input
        bind:group={choice}
        type="radio"
        id="choice5"
        name="file_choice"
        value="user_selected"
      />
      <label for="choice5">Choose your own file</label>
      {#if choice === "user_selected"}
        <input on:change={readFile} type="file" />
      {/if}
    </div>
  </div>
</div>
