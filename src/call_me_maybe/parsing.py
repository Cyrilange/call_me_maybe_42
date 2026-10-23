"""ABOUTME: parse the response"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from pydantic import ValidationError
from .model import FunctionDefinition


class Parsing:
    """Load function definitions and prepare function selection."""

    def get_the_prompt(self) -> str:
        """Return the user's prompt from command-line arguments."""
        return " ".join(sys.argv[1:])

    def read_json_file(self) -> List[FunctionDefinition]:
        """Load and validate the available function definitions."""
        path = (
            Path(__file__).resolve().parent.parent.parent
            / "data"
            / "input"
            / "functions_definition.json"
        )

        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)

        except (OSError, json.JSONDecodeError) as error:
            print(f"Unable to read function definitions: {error}")
            return []

        if not isinstance(data, list):
            print("Invalid JSON structure: expected a list.")
            return []

        functions: List[FunctionDefinition] = []

        try:
            for item in data:
                functions.append(
                    FunctionDefinition.model_validate(item)
                )
        except (ValidationError, ValueError, TypeError) as error:
            print(f"Invalid function definition: {error}")
            return []

        return functions

    def searching_the_right_function_tool(
        self,
        functions: List[FunctionDefinition],
    ) -> FunctionDefinition:
        """Select the appropriate function using the language model."""
        raise NotImplementedError(
            "Function selection has not been implemented yet."
        )
