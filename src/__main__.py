from typing import Any, Dict, List
import json

from call_me_maybe.model import Model
from call_me_maybe.parsing import Parsing
from call_me_maybe.functionDefinition import FunctionDefinition

def model_gen( model: Model, prompt: str, definitions: List[FunctionDefinition]) -> str:
    """Generate a function call in JSON format."""
    definitions_data = [
        function.model_dump(exclude={"full_definition"})
        for function in definitions
    ]

    full_prompt = (
        "You are a function-calling system, not a conversational assistant.\n"
        "Select exactly one function from the available definitions.\n"
        "Extract its parameters from the user's request.\n"
        "Do not answer the user's question.\n"
        "Do not explain your choice.\n"
        "Return only one valid JSON object with exactly these keys: "
        '"prompt", "name", "parameters".\n'
        f"Available functions:\n"
        f"{json.dumps(definitions_data, ensure_ascii=False)}\n"
        f"User request: {prompt}\n"
        "JSON:"
    )

    return model.generate(full_prompt)



def call_the_structred_functions( model: Model, prompt: str, definitions: List[Dict[str, Any]],) -> Dict[str, Any]:
    """Generate and parse the function-calling JSON response."""
    response = model_gen(model, prompt, definitions)

    try:
        result = json.loads(response)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"The model did not return valid JSON: {response}"
        ) from error

    if not isinstance(result, dict):
        raise ValueError("The model response must be a JSON object.")

    required_keys = {"prompt", "name", "parameters"}
    if set(result.keys()) != required_keys:
        raise ValueError(
            "The response must contain exactly: prompt, name, parameters."
        )
    result["prompt"] = prompt

    return result





def main() -> None:
    model = Model()
    parsing = Parsing()

    prompt = parsing.get_the_prompt()
    definitions = parsing.read_json_file()

    if not prompt:
        print("Error: please provide a prompt.")
        return

    if not definitions:
        print("Error: no function definitions were loaded.")
        return

    try:
        result = call_the_structred_functions(
            model,
            prompt,
            definitions,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except ValueError as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()