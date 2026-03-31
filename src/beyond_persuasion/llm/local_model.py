"""Adapter for the chosen local language model backend.

Keep this layer thin so the rest of the project does not depend on one vendor or library.
"""


class LocalLLMClient:
    """Placeholder interface for a local inference backend."""

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a model response."""
        raise NotImplementedError("Connect your local LLM backend here.")
