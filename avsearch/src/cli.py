import click
from typing import List

from .avsearch import AVSearch
from .utils import load_config


@click.command()
@click.option(
    "--targets",
    help="Comma separated list of YouTube videos, playlists or channels to transcribe",
    required=True,
)
@click.option("--quiet", help="Print out log messages with progress", default=False)
@click.option(
    "--algolia-app-id",
    help="Algolia App ID of your project (can also be set via the environment variable ALGOLIA_APP_ID)",
    default=None,
)
@click.option(
    "--algolia-index-name",
    help="Algolia Index name to upload the transcriptions to (can also be set via the environment variable ALGOLIA_INDEX_NAME)",
    default=None,
)
@click.option(
    "--algolia-api-key",
    help="Algolia Write API Key to upload the transcriptions with (can also be set via the environment variable ALGOLIA_API_KEY)",
    default=None,
)
@click.option(
    "--pattern-replace-json-file",
    help="JSON file of patterns to do find/replace operations on segments",
)
@click.option(
    "--categories-json-file",
    help="JSON file of categories to attempt categorization of segments",
)
@click.option(
    "--whisper-model",
    help="Whisper model to use for the transcription (https://alg.li/xaaQ26)",
    default="medium",
)
@click.option(
    "--youtube-dl-format",
    help="Format option to pass to YouTube DL to download source video in (https://alg.li/AwDfRu)",
    default="bestaudio[ext=m4a]",
)
@click.option(
    "--combine-short-segments/--no-combine-short-segments",
    help="Combine short segments of three words or less with the previous segment.",
    default=True,
)
@click.option(
    "--exit-on-error/--no-exit-on-error",
    help="Exit the entire process if one file has a download issue",
    default=True,
)
@click.option(
    "--remove-after-transcribe/--no-remove-after-transcribe",
    help="Remove the source audio file after transcription is complete",
    default=True,
)
def cli(
    targets: List[str],
    quiet: bool,
    algolia_app_id: str,
    algolia_index_name: str,
    algolia_api_key: str,
    pattern_replace_json_file: str,
    categories_json_file: str,
    whisper_model: str,
    youtube_dl_format: str,
    combine_short_segments: bool,
    exit_on_error: bool,
    remove_after_transcribe: bool,
):
    # If the configuration is not passed via an argument, load it via environment variables
    app_id, index_name, api_key = load_config(
        algolia_app_id, algolia_index_name, algolia_api_key
    )

    # Instantiate class
    avs = AVSearch(
        app_id,
        index_name,
        api_key,
        pattern_replace_json_file,
        categories_json_file,
        whisper_model,
        youtube_dl_format,
        combine_short_segments,
        remove_after_transcribe,
        exit_on_error,
        quiet,
    )

    # Run the transcription
    avs.transcribe(targets.split(","))
