"""ABOUTME: validate the function choosen """
import json
from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel, ValidationError, model_validator


class FunctionDefinition(BaseModel):
    """Represent and validate a function definition."""

    name: str
    description: str
    parameters: Dict[str, Dict[str, str]]
    returns: Dict[str, str]
    full_definition: str

    @model_validator(mode="after")
    def validation(self) -> "FunctionDefinition":
        """Check that each parameter has a type."""
        for name, details in self.parameters.items():
            if "type" not in details:
                raise ValueError(
                    f"Missing type for parameter {name} "
                    f"in function {self.name}"
                )
        return self


def get_functions_definition(
    path: Path,
) -> List[FunctionDefinition]:
    """Load and validate function definitions from a JSON file."""
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(
            f"Unable to read function definitions from {path}: {error}"
        ) from error

    if not isinstance(data, list) or not data:
        raise ValueError(
            "The function definition file must contain a non-empty list."
        )

    functions: List[FunctionDefinition] = []

    try:
        for item in data:
            if not isinstance(item, dict):
                raise ValueError(
                    "Each function definition must be a JSON object."
                )

            functions.append(
                FunctionDefinition(
                    name=item["name"],
                    description=item["description"],
                    parameters=item["parameters"],
                    returns=item["returns"],
                    full_definition=json.dumps(
                        item,
                        ensure_ascii=False,
                    ),
                )
            )
    except (KeyError, TypeError, ValidationError) as error:
        raise ValueError(
            f"Invalid function definition: {error}"
        ) from error

    return functions
