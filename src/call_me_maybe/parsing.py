
"""Parse command-line arguments and load function definitions."""

import argparse
import json
from pathlib import Path
from typing import List

from pydantic import ValidationError

from .functionDefinition import FunctionDefinition


class Parsing:
    """Load function definitions and prepare input arguments."""

    def parse_arguments(self) -> argparse.Namespace:
        """Parse CLI arguments."""
        parser = argparse.ArgumentParser(
            description="Introduction to function calling in LLMs"
        )

        parser.add_argument(
            "prompt",
            nargs="?",
            help="A single user request",
        )
        parser.add_argument(
            "--functions_definition",
            default="data/input/functions_definition.json",
            help="Path to the function definitions JSON file",
        )
        parser.add_argument(
            "--input",
            default="data/input/function_calling_tests.json",
            help="Path to the input JSON file",
        )
        parser.add_argument(
            "--output",
            default="data/output/function_calls.json",
            help="Path to the output JSON file",
        )

        return parser.parse_args()

    def read_json_file(
        self,
        path: str,
    ) -> List[FunctionDefinition]:
        """Load and validate function definitions."""
        try:
            with Path(path).open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(
                f"Unable to read function definitions: {error}"
            ) from error

        if not isinstance(data, list):
            raise ValueError("Expected a list of function definitions.")

        try:
            return [
                FunctionDefinition(
                    **item,
                    full_definition=json.dumps(
                        item,
                        ensure_ascii=False,
                    ),
                )
                for item in data
            ]
        except (ValidationError, ValueError, TypeError) as error:
            raise ValueError(
                f"Invalid function definition: {error}"
            ) from error
