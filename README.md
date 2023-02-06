# AVSearch

Automated YouTube Audio/Video content transcription search for your website

[Live demo](https://avsearch.vercel.com)

---

# Getting Started

## 1. Installation

```shell
# Install FFmpeg
brew install ffmpeg # MacOS
apt install ffmpeg # Linux
choco install ffmpeg # Windows (Chocolatey)

# Pip
python3 -m pip install git+https://github.com/algolia-samples/avsearch

# Wheel file (Download the latest release from https://github.com/algolia-samples/avsearch/releases)
python3 -m pip install avsearch-?.?.?-py3-none-any.whl

# From source
git clone https://github.com/algolia-samples/avsearch
cd avsearch

# https://python-poetry.org/docs/#installation
poetry install && poetry build

# Optionally, install the wheel file
python3 -m pip install ./dist/avsearch-?.?.?-py3-none-any.whl
# Or, use poetry's shell
poetry shell
```

## 2. Set up Algolia

To use this tool, you need an Algolia account. If you don't have one already, [create an account for free](https://www.algolia.com/users/sign-up). Note your [Application ID](https://www.algolia.com/doc/guides/sending-and-managing-data/manage-indices-and-apps/manage-your-apps/) during this process.

Once you have an account, your API Key can be located [here](https://www.algolia.com/account/api-keys/all). You don't need to create an Index to get started, Algolia will automatically create the index for us - just come up with a good name!

## 3. Usage via the command line

```shell
export ALGOLIA_APP_ID=<your-app-id>
export ALGOLIA_API_KEY=<your-api-key>
export ALGOLIA_INDEX_NAME=<your-index-name>
# Single video
av-search --targets "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
# Multiple videos
av-search --targets "https://youtu.be/dQw4w9WgXcQ,https://youtu.be/_C9PMLr_XC8"
```

## 4. Usage via Python

```shell
from avsearch import AVSearch

avs = AVSearch(app_id='AAAA1234', ...)
results = avs.transcribe(
    ["https://www.youtube.com/watch?v=zOz-Sk4K-64&list=PLuHdbqhRgWHLRlmvQ1OKLdjslSxXrAAjk"]
)
```

---

# Resources

- [Algolia Documentation](https://www.algolia.com/doc/)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [YouTube DL](https://github.com/ytdl-org/youtube-dl)

# Contributing

This project is open source and welcomes contributions. We only ask that you adhere to our [Code of Conduct](https://github.com/algolia-samples/.github/blob/master/CODE_OF_CONDUCT.md) when contributing and our process outlined below:

1. After completing your change, run the `scripts/pre-commit.sh` script to format and lint your code to fit our styling. This will run [Black](https://github.com/psf/black) and [Flake8](https://github.com/pycqa/flake8) automatically with our settings.
2. Submit a Pull Request with your changes and request approval.
3. Allow one week for your code to be reviewed by an Algolia team member. If changes are requested, these will need to be resolved before the changes are merged.

# Authors

- [Chuck Meyer, @chuckm](https://twitter.com/chuckm)
- [Michael King, @makvoid](https://twitter.com/makvoid)
