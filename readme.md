# Capturing Cancer with Music

Project that aims to imitate the process of cancer in a patient through a musical analogy.

## Using the script
Install [python-poetry](https://www.python-poetry.org). 
Run `poetry install` inside this directory, and then use the script via either `poetry run mutate_sheet [FILENAME]` or `poetry shell` and then `mutate_sheet [FILENAME]`.

## Developers
Make sure to use poetry to manage your dependencies, it'll make things a lot easier. 
When installing the project for the first time, be sure to run `poetry install -D` to get all the development tools.
Make sure to set up a proper editor (VSCode, NeoVim, etc.) that can take advantage of all of the automatic formatting and linting tools in the dev dependencies.
Run `poetry run uvicorn api.main:app --reload` to start the back-end server in development mode.
Move to the `front` directory in `api` and run `npm install && npm run dev` to start the Svelte development server.

## Deploying the server
Install python-poetry, then run `poetry install`. 
`fluidsynth` and `portaudio` must be installed for the back-end server to run.
Move into `api/front` and run `npm install && npm run build`.
In the top-level directory, `poetry run uvicorn src.api.main:app --host 0.0.0.0 --port [PORT]`.

You can also use docker instead. Run `docker build -t cancer_music . && docker run -p [PORT]:8000 -t cancer_music`. 

If you want uvicorn to run in https mode, copy over your certificates and keys before building. 
Then modify the `CMD` line in the `Dockerfile` to `poetry run uvicorn src.api.main:app --host 0.0.0.0 --ssl-keyfile=[KEYFILE] --ssl-certfile=[CERTFILE]`. 
Then, when running `docker run`, make sure to pass `-p 443:8000`.
