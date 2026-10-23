"""ABOUTME: Model wrapper for the call_me_maybe project."""

from typing import Dict, List
import json
from llm_sdk import Small_LLM_Model


class Model(Small_LLM_Model):
    """Extend Small_LLM_Model with project-specific helpers."""


    def get_tokens(self, text: str) -> List[str]:
        """Return the vocabulary tokens corresponding to the text.

        Args:
            text: The input text to tokenize.

        Returns:
            The vocabulary token strings.
        """
        try:
            ids = self.get_prompt_encode(text)

            if not ids:
                return []

            path = self.get_path_to_vocab_file()

            with open(path, "r", encoding="utf-8") as file:
                vocab = json.load(file)

            if not isinstance(vocab, Dict):
                raise ValueError("The vocabulary must be a JSON object.")

            id_to_token: Dict[int, str] = {
                token_id: token
                for token, token_id in vocab.items()
                if isinstance(token, str)
                and isinstance(token_id, int)
            }

            tokens: list[str] = []

            for token_id in ids:
                token = id_to_token.get(token_id)

                if token is None:
                    raise ValueError(
                        f"Token ID {token_id} not found in vocabulary."
                    )

                tokens.append(token)

            return tokens

        except (OSError, json.JSONDecodeError, TypeError,
                ValueError, RuntimeError) as e:
            print(f"Tokenization issue: {e}")
            return []


    def get_prompt_encode(self, text: str) -> List[int]:
        """Encode text and return its token IDs.

        Args:
            text: The input text to encode.

        Returns:
            A list of token IDs, or an empty list on error.
        """
        try:
            tokens = self.encode(text)
            return tokens[0].tolist()
        except (ValueError, TypeError, IndexError, RuntimeError) as e:
            print(f"Prompt encoding issue: {e}")
            return []

    def get_decode(self, ids: List[int]) -> str:
        """Decode token IDs into readable text.

        Args:
            ids: The token IDs to decode.

        Returns:
            The decoded text, or an empty string on error.
        """
        try:
            return self.decode(ids)
        except (ValueError, TypeError, IndexError, RuntimeError) as e:
            print(f"Decoding issue: {e}")
            return ""

    def get_logits(self, ids: List[int]) -> List[float]:
        """Return scores for possible next tokens.

        Args:
            ids: The input token IDs.

        Returns:
            The logits, or an empty list on error.
        """
        try:
            return self.get_logits_from_input_ids(ids)
        except (ValueError, TypeError, IndexError, RuntimeError) as e:
            print(f"Logits calculation issue: {e}")
            return []

    def get_next_token(self, ids: List[int]) -> int:
        """Select the token with the highest logit.

        Args:
            ids: The input token IDs.

        Returns:
            The selected token ID, or -1 if selection fails.
        """
        try:
            logits = self.get_logits(ids)

            if not logits:
                print("Next token selection issue: logits are empty.")
                return -1

            return max(
                range(len(logits)),
                key=lambda i: logits[i],
            )
        except (ValueError, TypeError, IndexError, RuntimeError) as e:
            print(f"Next token selection issue: {e}")
            return -1
        

    
    def generate(self, prompt: str, max_tokens: int = 100) -> str:
        """Generate text from a prompt, one token at a time.
        
        args: prompt, number of maximum tokens 
        
        return : the response in a  string
        """
        ids = self.get_prompt_encode(prompt)

        if not ids:
            return ""

        generated_ids: List[int] = []

        for _ in range(max_tokens):
            next_token = self.get_next_token(ids)

            if next_token == -1:
                break

            generated_ids.append(next_token)
            ids.append(next_token)

            #todo :  Stop if the model generates its end-of-sequence token.
            #todo :  We will need a reliable way to identify this token.

        return self.get_decode(generated_ids)

