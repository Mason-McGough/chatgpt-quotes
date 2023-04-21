# ChatGPT Quotes Plugin

![Graphic art of a bust generated with Stable Diffusion](static/logo.png)

A bare-bones ChatGPT plugin that retrieves thought-provoking quotes from famous figures throughout history.

For an in-depth walkthrough on this plugin, please read my article "ChatGPT Plugins Demystified: A Tutorial for Developers", which you can find on [my Medium page](https://medium.com/@masonmcgough).

## Setup

This project provides an API powered by FastAPI and built with Poetry. The following instructions can get you started.

1. Install [Python 3.10](https://www.python.org/downloads/).
2. Run the following commands:

```bash
python3 -m pip install poetry
poetry env use python3
poetry install
```

If you prefer to use an Anaconda virtual environment:

```bash
conda create -n chatgpt python=3.10  # Install Python 3.10
conda activate chatgpt               # Activate conda env
pip install poetry                   # Install Poetry
poetry env use `which python`        # Specify the Python binary
poetry install                       # Install dependencies
```

You should now be able to run the web server:

```bash
poetry run start
```

## Acknowledgements

Quotes were borrowed from the [inspirational-quotes](https://github.com/akhiltak/inspirational-quotes) repo.

## License

[MIT License](https://opensource.org/licenses/MIT)
