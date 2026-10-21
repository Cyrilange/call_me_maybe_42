"""ABOUTME: Model wrapper for the call_me_maybe project."""

from llm_sdk import Small_LLM_Model


class Model(Small_LLM_Model):
    """Extend Small_LLM_Model with project-specific helpers."""

    def get_tokens(self, text: str) -> list[str]:
        """Return the tokenizer pieces for the given text."""
        ids = self.get_prompt_encode(text)
        return self._tokenizer.convert_ids_to_tokens(ids)

    def get_prompt_encode(self, text: str) -> list[int]:
        """Encode the prompt and return its token IDs."""
        tokens = self.encode(text)
        return tokens[0].tolist()

    def get_decode(self, ids: list[int]) -> str:
        """Decode token IDs into readable text."""
        return self.decode(ids)
    
    def get_logits(self, ids: list[int]) -> list[float]:
        """Return the logits for the next token, scores of possible tokens"""
        return   self.get_logits_from_input_ids(ids)
    
    def get_next_token(self, ids: list[int]) -> int:
        """Select the token with the highest logit."""
        logits = self.get_logits(ids)
        return max(range(len(logits)), key=lambda i: logits[i])