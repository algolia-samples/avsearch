# AVSearch

Automated YouTube Audio/Video content transcription search for your website

---

# Getting Started

## 1. Installation

```shell
# Pip
python3 -m pip install git+https://github.com/algolia-samples/avsearch

# Wheel file (Download the latest release from https://github.com/algolia-samples/avsearch/releases)
python3 -m pip install avsearch-?.?.?-py3-none-any.whl

# From source
git clone https://github.com/algolia-samples/avsearch
cd avsearch
# https://python-poetry.org/docs/#installation
poetry install && poetry build
python3 -m pip install ./dist/avsearch-?.?.?-py3-none-any.whl
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
avs.transcribe(["https://www.youtube.com/watch?v=zOz-Sk4K-64&list=PLuHdbqhRgWHLRlmvQ1OKLdjslSxXrAAjk"])
```

---

# Resources

- [Algolia Documentation](https://www.algolia.com/doc/)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [YouTube DL](https://github.com/ytdl-org/youtube-dl)

# Contributing

This project is open source and welcomes contributions. We only ask that you adhere to our [Code of Conduct](https://github.com/algolia-samples/.github/blob/master/CODE_OF_CONDUCT.md) when contributing.

# Authors

- [Chuck Meyer, @chuckm](https://twitter.com/chuckm)
- [Michael King, @makvoid](https://twitter.com/makvoid)
