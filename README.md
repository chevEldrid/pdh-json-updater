This repo is for designing a script capable of automatically updating the format legality list for PDH using Scryfall's api

To set up a virtual environment for development, first [install pypoetry onto your machine](https://python-poetry.org/docs/#installation).
From there, you can [install your project dependencies](https://python-poetry.org/docs/basic-usage/#installing-dependencies) and
[run any scripts in the library](https://python-poetry.org/docs/basic-usage/#using-poetry-run) within the virtualenv. You can also
[build the contents of the repo into a python .whl](https://python-poetry.org/docs/cli#build) which can then be installed anywhere via `pip`

### Manual Override

Sometimes, the robots fail us and we have to take PDH into our own hands. Quick Commander_json manual update Guide.

1. Make sure [Poetry](https://python-poetry.org/docs/) is installed on your local machine, this is necessary to run the scripts
2. run `poetry install`, if you're on mac/windows you'll need `poetry install --no-dev` since dev dependencies aren't supported
3. run `poetry run python pdh_json_updater/update_json.py` from top of the repo, this is the main script that triggers the updates to pauper_commander.json
