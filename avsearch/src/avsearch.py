from algoliasearch.search_client import SearchClient
import json
import logging
import os
import re
from typing import List
import uuid
import whisper
import youtube_dl

from .utils import load_file
from .schemas import cleanup_patterns_schema, category_patterns_schema


class AVSearch:
    _model = None
    _downloaded = []
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

        # Setup custom logging format
        logging.basicConfig(
            level=logging.INFO, format="[A/V-Search] [%(levelname)s] %(message)s"
        )

        # Setup YouTube-DL options
        self.ytdl_opts = {
            "format": youtube_dl_format,
            "progress_hooks": [self._progress_hook],
        }

        # Setup our Algolia Client & Index
        self.client = SearchClient.create(app_id, api_key)
        self.index = self.client.init_index(index_name)

        # Load, parse and validate JSON files if needed:
        if pattern_replace_json_file:
            self._cleanup_patterns = load_file(
                pattern_replace_json_file, cleanup_patterns_schema
            )
        if categories_json_file:
            self._categories_patterns = load_file(
                categories_json_file, category_patterns_schema
            )

    def transcribe(self, urls: List[str]):
        self._downloaded.clear()

        # Download each video in the queue
        with youtube_dl.YoutubeDL(self.ytdl_opts) as ydl:
            ydl.download(urls)

        # Check if we were able to download everything if required
        if len(self._downloaded) != len(urls) and self.exit_on_error:
            if not self.quiet:
                logging.error(
                    "Error: An error occurred downloading a file and exit_on_error was set to True!"
                )
            return

        # Ensure the model has been loaded
        if not self._model:
            self._setup_model()

        # For each file downloaded, transcribe the audio file
        transcriptions = []
        for file in self._downloaded:
            file = file.decode("utf-8")
            if not self.quiet:
                logging.info(f"Starting transcription of: {file}")
            result = self._model.transcribe(file)
            transcriptions.append(
                list(
                    map(
                        lambda segment: self._parse_segment(file, segment),
                        self._combine_segments(result["segments"])
                        if self.combine_short_segments
                        else result["segments"],
                    )
                )
            )
            if self.remove_after_transcription:
                os.unlink(file)

        # Flatten the list of lists into a single list
        transcriptions = [item for sub in transcriptions for item in sub]

        # Save the transcriptions into our Algolia Index
        self.index.save_objects(transcriptions).wait()

        # All done!
        if not self.quiet:
            logging.info(
                f"Successfully saved {len(transcriptions)} transcription segments into your Index."
            )
        return transcriptions

    def _setup_model(self) -> None:
        if not self.quiet:
            logging.info(
                f"Loading Whisper's {self.whisper_model} model, please wait..."
            )
        self._model = whisper.load_model(self.whisper_model)

    def _progress_hook(self, file) -> None:
        # Update the list once it has finished downloading
        if file["status"] == "finished":
            self._downloaded.append(file["filename"].encode("utf-8"))

    def _parse_segment(self, file: str, segment):
        chunks = file.split(".")[0].split("-")
        video_id = chunks.pop()
        video_title = "-".join(chunks)
        return {
            "objectID": str(uuid.uuid4()),
            "videoID": video_id,
            "videoTitle": video_title,
            "text": segment["text"].strip(),
            "start": round(segment["start"], 2),
            "end": round(segment["end"], 2),
            "categories": self._categorize_segment(segment["text"]),
        }

    def _combine_segments(self, segments):
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
            lambda pat: pat["category"]
            if re.search(pat["symbol"], text, flags=re.I)
            else None,
            self._categories_patterns,
        )
        return list(filter(lambda val: val is not None, categories))

    def _cleanup_text(self, text: str) -> str:
        for sub in self._cleanup_patterns:
            text = re.sub(sub["symbol"], sub["value"], text, flags=re.I)
        return text
