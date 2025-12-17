from algoliasearch.search_client import SearchClient
import logging
import os
from pathlib import PosixPath
import re
from typing import List
import whisper
import youtube_dl
import json

from .utils import load_file
from .schemas import cleanup_patterns_schema, category_patterns_schema

class AVSearch:
    _model = None
    _downloaded = []
    _file_errors = []
    _cleanup_patterns = []
    _categories_patterns = []

    def __init__(
        self,
        app_id: str = None,
        index_name: str = None,
        api_key: str = None,
        pattern_replace_json_file: str = None,
        categories_json_file: str = None,
        whisper_model: str = "medium",
        youtube_dl_format: str = "bestaudio[ext=m4a]",
        use_download_archive: bool = False,
        combine_short_segments: bool = True,
        remove_after_transcription: bool = True,
        exit_on_error: bool = True,
        quiet: bool = False,
    ) -> None:
        self.whisper_model = whisper_model
        self.combine_short_segments = combine_short_segments
        self.remove_after_transcription = remove_after_transcription
        self.exit_on_error = exit_on_error
        self.quiet = quiet
        self.use_download_archive = use_download_archive

        # Setup custom logging format
        logging.basicConfig(
            level=logging.INFO,
            format="[A/V-Search] [%(levelname)s] %(message)s",
        )

        # Setup YouTube-DL options
        self.ytdl_opts = {"format": youtube_dl_format, "progress_hooks": [self._progress_hook]}
        if self.use_download_archive:
            self._setup_download_archive()

        # Setup our Algolia Client & Index
        self.client = SearchClient.create(app_id, api_key)
        self.index = self.client.init_index(index_name)

        # Load, parse and validate JSON files if needed:
        if pattern_replace_json_file:
            self._cleanup_patterns = load_file(pattern_replace_json_file, cleanup_patterns_schema)
        if categories_json_file:
            self._categories_patterns = load_file(categories_json_file, category_patterns_schema)

    def transcribe(self, urls: List[str]) -> List[dict]:
        self._downloaded.clear()
        self._file_errors.clear()

        # Download each video and it's metadata in the queue
        with youtube_dl.YoutubeDL(self.ytdl_opts) as ydl:
            all_metadata = ydl.extract_info(urls[0])

        # Check if we were able to download everything if required
        if len(self._file_errors) > 0 and self.exit_on_error:
            if not self.quiet:
                logging.error(
                    f"""Error: An error occurred downloading and exit_on_error was set to True!
                     ({', '.join(self._file_errors)})"""
                )
            return

        # Ensure the model has been loaded
        if not self._model:
            self._setup_model()

        # For each file downloaded, transcribe the audio file
        transcriptions = []
        for file in self._downloaded:
            file = file.decode("utf-8")

            # Extract metadata if a single video
            if "entries" not in all_metadata:
                metadata = all_metadata
            # Extract specific video metadata if a playlist is used
            else:
                metadata = next(
                    filter(
                        lambda entry: entry["id"] == self._get_video_id(file),
                        all_metadata["entries"],
                    ),
                    None,
                )
                if metadata is None:
                    if not self.quiet:
                        logging.error(f"Unable to locate metadata record for file, can't process video: {file}")
                    return

            # Transcription / Parsing
            if not self.quiet:
                logging.info(f"Starting transcription of: {file}")
            result = self._model.transcribe(file)

            # Save transcription to text file
            with open("transcription.txt", "a") as out_file:
                out_file.write(json.dumps(result))

            transcriptions.append(
                list(
                    map(
                        lambda segment: self._parse_segment(metadata, segment),
                        self._combine_segments(result["segments"])
                        if self.combine_short_segments
                        else result["segments"],
                    )
                )
            )
            if self.remove_after_transcription:
                os.unlink(file)

        if not self.quiet:
            logging.info("Done transcribing videos, starting sync to Algolia.")

        # Flatten the list of lists into a single list
        transcriptions = [item for sub in transcriptions for item in sub]

        # Create the context links for each transcription
        self._link_context(transcriptions)
        
        # Break the records into 10k record chunks
        chunks = [transcriptions[i : i + 10000] for i in range(0, len(transcriptions), 10000)]  # noqa: E203

        # Save the transcription chunks into our Algolia Index
        for chunk in chunks:
            self.index.save_objects(chunk).wait()

        # All done!
        if not self.quiet:
            logging.info(f"Successfully saved {len(transcriptions)} transcription segments into your Index.")
        return transcriptions

    def _link_context(self, transcriptions: List[dict]) -> None:
        for index, transcription in enumerate(transcriptions):
            before = { 'start': 0, 'text': '' }
            after = { 'start': transcriptions[index]['end'], 'text': '' }
            # Grab the preceding context (if not the first record)
            if index != 0:
                context = transcriptions[index - 1]
                before = {
                    'start': context['start'],
                    'text': context['text']
                }
            # Grab the succeeding context (if not the last record)
            if index != len(transcriptions) - 1:
                context = transcriptions[index + 1]
                after = {
                    'start': context['start'],
                    'text': context['text']
                }
            # Add the context to the record
            transcription['context'] = {
                'before': before,
                'after': after
            }

    def _setup_model(self) -> None:
        if not self.quiet:
            logging.info(f"Loading Whisper's {self.whisper_model} model, please wait...")
        self._model = whisper.load_model(self.whisper_model)

    def _progress_hook(self, file: dict) -> None:
        # Check if an error occurred
        if file["status"] not in ["downloading", "finished"]:
            self._file_errors.append(file["filename"])
        # Update the list once it has finished downloading
        if file["status"] == "finished":
            self._downloaded.append(file["filename"].encode("utf-8"))

    def _parse_segment(self, meta: dict, segment: dict) -> dict:
        return {
            "objectID": f"{meta['id']}-{segment['id']}",
            "videoID": meta["id"],
            "videoTitle": meta["title"],
            "videoDescription": meta["description"],
            "url": f'https://youtu.be/{meta["id"]}?t={round(segment["start"], 2):.0f}',
            "thumbnail": meta["thumbnails"][0]["url"],
            "text": segment["text"].strip(),
            "start": round(segment["start"], 2),
            "end": round(segment["end"], 2),
            "categories": self._categorize_segment(segment["text"]),
        }

    def _combine_segments(self, segments: List[dict]) -> List[dict]:
        stale_indexes = []
        for index, segment in enumerate(segments):
            segment["text"] = self._cleanup_text(segment["text"].strip())
            # If any segment is three words or smaller, combine it with the previous segment
            if len(segment["text"].split(" ")) <= 3:
                stale_indexes.append(index)
                new_segment = segments[index - 1]
                new_segment["text"] += f" {segment['text']}"
                new_segment["end"] = segment["end"]
        # Remove any stale indexes in reverse order (or else they will not be the same)
        for index in sorted(stale_indexes, reverse=True):
            segments.pop(index)
        return segments

    def _categorize_segment(self, text: str) -> List[str]:
        categories = map(
            lambda pat: pat["category"] if re.search(pat["symbol"], text, flags=re.I) else None,
            self._categories_patterns,
        )
        return list(filter(lambda val: val is not None, categories))

    def _cleanup_text(self, text: str) -> str:
        for sub in self._cleanup_patterns:
            text = re.sub(sub["symbol"], sub["value"], text, flags=re.I)
        return text

    def _get_video_id(self, file: str) -> str:
        groups = re.search(r".+-([A-Za-z0-9_\-]{11}).m4a", file).groups()
        if not len(groups):
            return None
        return groups[0]

    def _setup_download_archive(self) -> None:
        path = PosixPath("~/.config/algolia").expanduser().resolve()
        # Create the directory if it doesn't exist yet
        path.mkdir(parents=True, exist_ok=True)
        self.ytdl_opts["download_archive"] = PosixPath(f"{path}/.avsearch-archive")
