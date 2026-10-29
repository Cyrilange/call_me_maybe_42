from typing import Any, Dict, List
import json
from pathlib import Path
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
    parsing = Parsing()
    args = parsing.parse_arguments()

    try:
        definitions = parsing.read_json_file(
            args.functions_definition
        )

        if not definitions:
            raise ValueError("No function definitions were loaded.")

        model = Model()

        if args.prompt:
            result = call_the_structred_functions(
                model,
                args.prompt,
                definitions,
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return

        input_path = Path(args.input)
        with input_path.open("r", encoding="utf-8") as file:
            tests = json.load(file)

        if not isinstance(tests, list):
            raise ValueError("The input JSON must contain a list.")

        results = []
        for test in tests:
            if isinstance(test, str):
                prompt = test
            elif isinstance(test, dict):
                prompt = test.get("prompt", test.get("input"))
            else:
                raise ValueError("Invalid test entry.")

            if not isinstance(prompt, str) or not prompt.strip():
                raise ValueError("A test is missing its prompt.")

            results.append(
                call_the_structred_functions(
                    model,
                    prompt,
                    definitions,
                )
            )

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(results, file, indent=2, ensure_ascii=False)

        print(f"Results written to {output_path}")

    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(f"Error: {error}")

if __name__ == "__main__":
    main()