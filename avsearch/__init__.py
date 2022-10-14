from .src.avsearch import AVSearch
from .src.cli import cli
from .src.errors import (
    MissingConfigurationError,
    MissingConfigurationFileError,
    InvalidFileSchemaError,
)
from .src.schemas import category_patterns_schema, cleanup_patterns_schema

__version__ = "0.1.0"
