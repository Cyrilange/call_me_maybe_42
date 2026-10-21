import sys
from call_me_maybe.model import Model

def main() -> None:
    model = Model()
    prompt = " ".join(sys.argv[1:])
    print(f"Prompt: {prompt}")
    print(f"Tokens: {model.get_tokens(prompt)}")
    print(f"Token IDs: {model.get_prompt_encode(prompt)}")


if __name__ == "__main__":
    main()