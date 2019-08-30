## Dev Environment

Using [`pyenv`](https://github.com/pyenv/pyenv) (optional), and [`poetry`](https://poetry.eustace.io/) to manage deps.

> `poetry` is used to build our Docker containers, and guarantees all deps **and sub-deps** are pinned to specific versions.

If you don't want to add, remove, or update deps, this part isn't strictly necessary. It's also a bit of a PITA the first time, but comes with serious benefits: you get linting, type checking, and code completion for an environment (Python version + deps) that exactly matches the environment inside the Docker container.

First, install `pyenv`, and use it to install Python X.X.X:

```sh
# on OSX
brew install pyenv

# or, use system python as long as it's in $PATH
pyenv install X.X.X

# have pyenv ensure this Python version is always first in $PATH in project directory
pyenv local X.X.X
```

Then, install `poetry`, and tell it to use your newly installed Python X.X.X for this project:

```sh
curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
poetry self:update --preview

# cd into project directory
poetry env use 3.7

# install deps with poetry
poetry install
```

#### Run Dev Server

```sh
poetry run uvicorn src.main:app --reload
```

### Enabling Editor Support

For jedi, mypy, and flake8.

#### Sublime Text

From inside the repo, run `poetry run which python` to get the path of the `python` executable in virtual env created by `poetry`.

Then, open your project settings and insert the following:

```json
{
  "folders": [
    // ...
  ],
  "settings": {
    "python_interpreter": "/path/to/python",
    "SublimeLinter.linters.flake8.executable": "/path/to/flake8",
    "SublimeLinter.linters.mypy.executable": "/path/to/mypy"
  }
}
```
