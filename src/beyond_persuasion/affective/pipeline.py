"""Affective computing pipeline.

Suggested responsibilities:
- load a pretrained text emotion model,
- normalize labels to the project's taxonomy,
- return structured predictions usable by the ethical engine.
"""

from beyond_persuasion.schemas import EmotionPrediction


class EmotionAnalyzer:
    """Wrapper around the future emotion classification model."""

    def predict(self, text: str) -> EmotionPrediction:
        """Estimate the emotional state of a single user utterance."""
        raise NotImplementedError("Implement emotion inference here.")
