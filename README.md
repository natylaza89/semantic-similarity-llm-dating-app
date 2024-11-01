# Semantic Similarity LLM Dating App

A Backend Oriented project which its server using Python 3.12, FastAPI, WebSockets, CoHere, Gemini 1.5 Flash & Embeddings.
A simple client uses Python 3.12 & click.

### Install Python 3.12

```bash
# This works for macOS
> brew install pyenv
# The rest of the commands can work for both mac and linux)
> pyenv install 3.12
> vim  ~/.zshrc
# insert those lines
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
```

### Create Virtual Environment

##### Need to create virtual environment on both apps in the next paths:

1. `{PROJECT_PATH}/backend`
2. `{PROJECT_PATH}/client`

after running those commands there will be a ".venv" within the mentioned paths

```bash
> pyenv local 3.12.2 # use python 3.12
> pip install poetry==1.8.2
> poetry env use -vv 3.12.2
> poetry shell # activate venv
```

### Install Dev Dependencies

```bash
> poetry install -vvvv
> poetry show # show project packages
```

### Run Dev Utils ( Linter, Formatter & Type Checker - configuration in pyproject.toml)

```bash
# Linter
> cd {PROJECT_PATH}/backend && poetry run ruff check .
# Formatter
> cd {PROJECT_PATH}/backend && poetry run ruff format .
# Type Checker
> cd {PROJECT_PATH}/backend && poetry run mypy ./app --explicit-package-bases
```

### Run The Applications

#### Server:

```bash
1. Make sure to get an api key from [CoHere](https://cohere.com/) & update .env File with `COHERE_API_KEY=<KEY>` - if you choose not to configure in .env the `MOCK_SEMANTIC_SIMILARITY=true`
2. Make sure you get an api key from [Gemini](https://aistudio.google.com/app/apikey) & update .env File with `GEMINI_API_KEY=<KEY>`
3. cd {PROJECT_PATH}/backend && poetry run python app/main.py
```

#### Client:

Open 2 terminals and make sure to follow this procedure's pattern:
tab 1:

```bash
1. cd {PROJECT_PATH}/client
2. poetry run python3 app/main.py register --user-id naty --name naty --description king
3. poetry run python3 app/main.py chat --user-id naty --preferences queen
```

tab 2:

```bash
1. cd {PROJECT_PATH}/client
2. poetry run python3 app/main.py register --user-id nofar --name nofar --description queen
3. poetry run python3 app/main.py chat --user-id nofar --preferences king
```


### License
This project is under a modified Non-Commercial Open Source License. 

You can use and modify it freely for non-commercial purposes, but commercial use is not permitted. See [LICENSE](LICENSE) file for details.

![License: Non-Commercial](https://img.shields.io/badge/License-Non_Commercial-blue.svg)
