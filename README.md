*This project has been created as part of the 42 curriculum by Cyrilange.*

# Call Me Maybe

## Description

**Call Me Maybe** is a project focused on understanding and implementing function calling with Large Language Models (LLMs).

The goal is to build a system that allows an LLM to interpret a user's request, select the appropriate function from a list of available functions, extract the required parameters, and generate a structured JSON response.

Instead of answering the user directly, the model must identify which function should be called and return the corresponding arguments.

The project uses a locally loaded Hugging Face language model through a custom SDK built on top of PyTorch and Transformers.

### Main objectives

- Understand how LLMs generate text token by token.
- Understand function calling and structured outputs.
- Select the correct function according to a user request.
- Extract function parameters from natural language.
- Generate structured JSON responses.
- Explore constrained decoding and its role in controlling model outputs.

## Instructions

### Requirements

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/)
- Internet connection for the initial model download
- Sufficient RAM or GPU memory to load the language model

### Installation

Clone the repository:

```bash
git clone https://github.com/Cyrilange/call_me_maybe_42.git
cd call_me_maybe_42
```

Install the project dependencies:

```bash
make install
```

This command uses `uv sync` to create the virtual environment and install the required dependencies.

### Execution

Run the program with a custom prompt:

```bash
uv run python -m src "What is the sum of 2 and 3?"
```

Run the complete set of predefined examples:

```bash
make run-all
```

The default input file is:

```text
data/input/function_calling_tests.json
```

Function definitions are stored in:

```text
data/input/functions_definition.json
```

The generated results are written to:

```text
data/output/function_calls.json
```

### Available commands

| Command | Description |
|---|---|
| `make install` | Install dependencies |
| `make run` | Run the program |
| `make run-all` | Run all predefined examples |
| `make debug` | Start the debugger |
| `make lint` | Run code quality checks |
| `make clean` | Remove temporary files |
| `make fclean` | Remove temporary files and virtual environment |
| `make re` | Clean and reinstall |

## Algorithm Explanation

### 1. Function definitions

The system starts by loading the available function definitions from a JSON file.

Each function contains:

- A name.
- A description.
- A list of parameters and their types.
- A return type.

For example:

```json
{
    "name": "fn_add_numbers",
    "description": "Add two numbers together and return their sum.",
    "parameters": {
        "a": {
            "type": "number"
        },
        "b": {
            "type": "number"
        }
    },
    "returns": {
        "type": "number"
    }
}
```

The definitions are validated using Pydantic before being passed to the model.

### 2. Prompt construction

The user's request and the available function definitions are combined into a prompt.

The model receives instructions to:

- Select exactly one available function.
- Extract the required parameters.
- Avoid answering the user's request directly.
- Return a JSON object containing exactly three keys: `prompt`, `name`, and `parameters`.

### 3. Token generation

The model generates its response one token at a time.

The project uses a greedy decoding strategy:

1. Encode the prompt into token IDs.
2. Retrieve the logits for the next token.
3. Select the token with the highest logit.
4. Append the selected token to the generated sequence.
5. Repeat until a valid JSON object is detected or the maximum number of tokens is reached.

### 4. Constrained decoding

Constrained decoding is a technique that restricts the tokens a language model can generate according to predefined rules.

The general principle is to filter the model's possible next tokens at every generation step.

For example, suppose the expected output is:

```json
{
    "prompt": "What is 2 + 3?",
    "name": "fn_add_numbers",
    "parameters": {
        "a": 2,
        "b": 3
    }
}
```

The constraints should ensure that:

- The output is a valid JSON object.
- The required keys are present.
- The function name belongs to the available function definitions.
- The parameters match the selected function's definition.
- Parameter values respect their expected types.
- Unexpected properties are rejected.

A genuine constrained decoding algorithm can be described as follows:

1. Define the allowed output structure.
2. Track the tokens generated so far.
3. Determine which tokens can legally follow the current sequence.
4. Mask the logits of forbidden tokens, typically by assigning negative infinity.
5. Select the next token from the remaining allowed tokens.
6. Repeat until the output is complete.

This approach prevents invalid structures from being generated instead of simply detecting errors afterwards.

**Current implementation:** the project currently uses greedy decoding and checks whether the generated text forms valid JSON. It does not yet implement token-level constrained decoding or logit masking. These are distinct mechanisms and represent an area for further development.

### 5. JSON parsing and validation

After generation, the response is parsed using Python's `json.loads()`.

The program checks that:

- The response is valid JSON.
- The response is a dictionary.
- The dictionary contains exactly the required keys.

The original user prompt is then assigned to the `prompt` field.

## Design Decisions

### Local model inference

The project uses a custom SDK built on Hugging Face Transformers and PyTorch.

This allows the model to run locally rather than relying on an external inference API.

### Greedy decoding

Greedy decoding was chosen as a straightforward generation strategy.

At each step, the model selects the token with the highest logit.

This makes the generation process deterministic for a fixed model and prompt, assuming identical execution conditions.

### Pydantic

Pydantic is used to validate function definitions before they are sent to the model.

This helps detect missing or incorrectly structured function parameters.

### JSON output

JSON was chosen because it is easy to generate, parse, validate, and exchange between different components.

## Performance Analysis

The project evaluates the quality and reliability of generated function calls.

### Accuracy

The accuracy of the system depends on the model's ability to:

- Understand the user's request.
- Select the appropriate function.
- Extract the correct arguments.
- Follow the expected JSON structure.

A valid JSON response does not necessarily mean that the selected function or its arguments are correct.

### Speed

The model generates tokens sequentially.

The generation speed depends on:

- Model size.
- Available hardware.
- Input prompt length.
- Number of generated tokens.

Local inference avoids external API calls but requires sufficient computational resources.

### Reliability

JSON parsing and structural checks help detect malformed responses.

However, these checks happen after generation and cannot guarantee that the model will always produce a valid function call.

Token-level constrained decoding could improve structural reliability by preventing forbidden tokens during generation.

No quantitative performance benchmarks are currently reported.

## Challenges Faced

### Generating valid JSON

One of the main challenges is getting a language model to return structured JSON instead of natural language explanations.

The prompt explicitly instructs the model to return only the required JSON object.

The generated response is then parsed and checked using Python.

### Token-by-token generation

Understanding how models generate text requires understanding tokenization, token IDs, logits, and decoding strategies.

The project uses these concepts to implement its own generation loop.

### Function selection

The model must distinguish between several available functions and select the one that best matches the user's request.

Providing clear function descriptions and parameter definitions helps guide this selection.

### Constrained decoding

Another challenge is ensuring that generated tokens respect a predefined structure.

A future improvement is to implement token-level constraints that filter invalid tokens before they are selected.

## Testing Strategy

The project includes predefined prompts in:

```text
data/input/function_calling_tests.json
```

These examples cover different function-calling scenarios:

- Adding numbers.
- Greeting a person.
- Reversing a string.
- Calculating square roots.
- Replacing text using regular expressions.

The predefined tests are executed using:

```bash
make run-all
```

The generated results are saved in:

```text
data/output/function_calls.json
```

The validation strategy focuses on:

- Checking that the output is valid JSON.
- Checking that the output contains the expected keys.
- Checking that function definitions contain valid parameter types.
- Checking whether the selected function and extracted parameters match the expected result.

Further automated tests should compare generated function calls against expected outputs and measure the accuracy of function selection and parameter extraction.

## Example Usage

### Example 1: Addition

**Input:**

```text
What is the sum of 2 and 3?
```

**Expected function call:**

```json
{
    "prompt": "What is the sum of 2 and 3?",
    "name": "fn_add_numbers",
    "parameters": {
        "a": 2,
        "b": 3
    }
}
```

### Example 2: Reverse a string

**Input:**

```text
Reverse the string 'hello'
```

**Expected function call:**

```json
{
    "prompt": "Reverse the string 'hello'",
    "name": "fn_reverse_string",
    "parameters": {
        "s": "hello"
    }
}
```

### Example 3: Calculate a square root

**Input:**

```text
What is the square root of 144?
```

**Expected function call:**

```json
{
    "prompt": "What is the square root of 144?",
    "name": "fn_get_square_root",
    "parameters": {
        "a": 144
    }
}
```

*These are expected examples of the generated structure, not guaranteed outputs from every model execution.*

## Resources

### Documentation

- [Hugging Face Transformers](https://huggingface.co/docs/transformers/index)
- [Hugging Face Hub](https://huggingface.co/docs/huggingface_hub/index)
- [PyTorch Documentation](https://pytorch.org/docs/stable/index.html)
- [Pydantic Documentation](https://docs.pydantic.dev/latest/)
- [Python JSON Documentation](https://docs.python.org/3/library/json.html)
- [JSON Schema Documentation](https://json-schema.org/learn/getting-started-step-by-step)

### Articles and concepts

- [Constrained Decoding](https://arxiv.org/abs/2307.09702)
- [Language Models and Tokenization](https://huggingface.co/learn/nlp-course/chapter6/1)

### AI Usage

AI tools were used as learning and documentation assistants during this project.

They were used for:

- Understanding function calling concepts and constrained decoding.
- Clarifying token generation, tokenization, and logits.
- Helping organize technical explanations.
- Reviewing the structure and wording of the README.

AI-generated explanations and suggestions were treated as learning resources. The project implementation and final technical decisions remain the responsibility of the student.
