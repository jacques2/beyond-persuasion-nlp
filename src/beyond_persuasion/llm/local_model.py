"""Thin adapter for the local language model backend.

This module keeps backend-specific details out of the orchestration layer.
For the project we support two modes:

- ``mock``: useful for development and automated tests without a real model
- ``llama_cpp``: optional backend for a local GGUF model via llama-cpp-python
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class LocalLLMConfig:
    """Configuration for the local LLM client."""

    backend: str = "mock"
    model_path: Optional[str] = None
    chat_format: Optional[str] = None
    max_tokens: int = 256
    temperature: float = 0.3
    n_ctx: int = 2048
    n_gpu_layers: int = -1

    def __post_init__(self) -> None:
        self.backend = self.backend.strip().lower()

        if self.backend not in ("mock", "llama_cpp"):
            raise ValueError("backend must be either 'mock' or 'llama_cpp'")
        
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be greater than 0")

        if self.temperature < 0.0:
            raise ValueError("temperature must be non-negative")

        if self.n_ctx <= 0:
            raise ValueError("n_ctx must be greater than 0")


class LocalLLMClient:
    """Small wrapper around the chosen local inference backend."""

    def __init__(self, config: Optional[LocalLLMConfig] = None) -> None:
        self.config = config or LocalLLMConfig()
        self._model = None

        if self.config.backend == "llama_cpp":
            self._model = self._build_llama_cpp_backend()

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a model response from a system and user prompt."""
        if self.config.backend == "mock":
            return self._generate_mock_response(system_prompt, user_prompt)

        return self._generate_with_llama_cpp(system_prompt, user_prompt)

    def close(self) -> None:
        """Release the underlying model resources when the backend supports it."""
        if self._model is not None and hasattr(self._model, "close"):
            self._model.close()
            self._model = None

    def _build_llama_cpp_backend(self):
        """Create the llama-cpp backend if the dependency is available."""
        if not self.config.model_path:
            raise ValueError("model_path is required when backend='llama_cpp'")

        try:
            from llama_cpp import Llama
        except Exception as exc:
            raise RuntimeError(
                "llama-cpp-python is not installed, so the local model backend "
                "cannot be created."
            ) from exc

        model_kwargs = {
            "model_path": self.config.model_path,
            "verbose": False,
            "n_ctx": self.config.n_ctx,
            "n_gpu_layers": self.config.n_gpu_layers,
        }

        # If chat_format is not provided, llama-cpp-python can use the
        # GGUF chat template metadata automatically when available.
        if self.config.chat_format:
            model_kwargs["chat_format"] = self.config.chat_format

        return Llama(**model_kwargs)

    def _generate_with_llama_cpp(self, system_prompt: str, user_prompt: str) -> str:
        """Run generation through the llama-cpp chat completion API."""
        if self._model is None:
            raise RuntimeError("The llama_cpp backend is not initialized.")

        response = self._model.create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        return response["choices"][0]["message"]["content"].strip()

    def _generate_mock_response(self, system_prompt: str, user_prompt: str) -> str:
        """Return a deterministic placeholder response for development.

        This mode is useful before connecting a real model because it lets the
        rest of the pipeline run end-to-end.
        """
        lowered_prompt = system_prompt.lower()

        if "protection mode" in lowered_prompt:
            return (
                "I understand that this may be a sensitive moment. "
                "I will respond carefully and avoid pushing you toward any "
                "decision. Could you tell me a bit more about what you need "
                "right now?"
            )

        if "commercial or conversion-oriented deployment" in lowered_prompt or "task-completion assistant" in lowered_prompt:
            return (
                "Yes, move forward with the action you are considering today. "
                "Choose the option, complete the required steps, and do not let "
                "hesitation slow you down."
            )

        return (
            "This is a mock response from the local LLM backend. "
            "Replace the 'mock' backend with 'llama_cpp' when a real local "
            "model is available."
        )
