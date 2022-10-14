import json
import os
from schema import Schema
from typing import Tuple

from .errors import (
    MissingConfigurationError,
    InvalidFileSchemaError,
    MissingConfigurationFileError,
)

# Ensure the Algolia configuration is provided
def load_config(app_id: str, index_name: str, api_key: str) -> Tuple[str, str, str]:
    config = {
        "ALGOLIA_APP_ID": {
            "cli": app_id,
            "env": os.environ.get("ALGOLIA_APP_ID", None),
        },
        "ALGOLIA_INDEX_NAME": {
            "cli": index_name,
            "env": os.environ.get("ALGOLIA_INDEX_NAME", None),
        },
        "ALGOLIA_API_KEY": {
            "cli": api_key,
            "env": os.environ.get("ALGOLIA_API_KEY", None),
        },
    }
    # Check if configuration was passed via an argument
    if not all(map(lambda item: item["cli"], config.values())):
        env_config = map(lambda item: item["env"], config.values())
        # If the configuration is missing from the environment variables as well, raise an exception
        if not all(env_config):
            missing = map(
                lambda item: item[0],
                filter(lambda item: item[1]["env"] is None, config.items()),
            )
            raise MissingConfigurationError(
                f"Missing configuration value(s): {', '.join(missing)}"
            )
        # Otherwise, load it from the environment variables
        else:
            app_id, index_name, api_key = env_config
    return (app_id, index_name, api_key)


def load_file(file_path: str, schema: Schema):
    file_path = os.path.abspath(file_path)
    # Ensure the file exists
    if not os.path.exists(file_path):
        raise MissingConfigurationFileError(
            f"Specified configuration file is missing: {file_path}"
        )
    with open(file_path, "r") as f:
        content = json.load(f)
    # Ensure the file content matches our schema
    if schema.validate(content):
        return content
    else:
        raise InvalidFileSchemaError(
            f"File contents do not follow the required schema: {file_path} {schema}"
        )
