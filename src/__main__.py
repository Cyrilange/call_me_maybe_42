from call_me_maybe.model import Model
from call_me_maybe.parsing import Parsing



def model_gen():
    pass

def call_the_structred_functions():
     pass

def main() -> None:
    model = Model()
    parsing = Parsing()
    prompt = parsing.get_the_prompt()
    print(f"Tokens: {model.get_tokens(prompt)}")
    print(f"Token IDs: {model.get_prompt_encode(prompt)}")
    print(f"Next token: {model.get_next_token(model.get_prompt_encode(prompt))}")
    definitions = parsing.read_json_file()
    print(definitions)


if __name__ == "__main__":
    main()