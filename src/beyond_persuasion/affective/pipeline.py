"""Affective computing pipeline for the project.

The goal of this module is to provide one clear interface for emotion
prediction.

Design choice:
- if a Hugging Face classifier is available, use it;
- otherwise, fall back to a transparent keyword-based heuristic.

This keeps the system usable during development and makes the behavior easy
to explain in the report.

The project is English-only, so the heuristic fallback is also restricted
to English input.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from beyond_persuasion.affective.preprocessing import normalize_text
from beyond_persuasion.schemas import EmotionPrediction


PROJECT_EMOTIONS = ("sadness", "anger", "fear", "stress", "neutral")


@dataclass
class EmotionAnalyzerConfig:
    """Configuration for the emotion analysis pipeline."""

    model_name: Optional[str] = None
    use_transformers: bool = True
    candidate_labels: Sequence[str] = field(default_factory=lambda: PROJECT_EMOTIONS)


class EmotionAnalyzer:
    """Predict a project-level emotion label from user text.

    The analyzer exposes a single public method, ``predict``, so the rest of
    the repository does not need to know whether predictions come from a model
    or from the heuristic fallback.
    """

    def __init__(self, config: Optional[EmotionAnalyzerConfig] = None) -> None:
        self.config = config or EmotionAnalyzerConfig()
        self._classifier = None

        if self.config.use_transformers:
            self._classifier = self._build_transformers_pipeline()

    def predict(self, text: str) -> EmotionPrediction:
        """Estimate the emotional state of a single user utterance."""
        cleaned_text = normalize_text(text)

        if not cleaned_text:
            return EmotionPrediction(
                label="neutral",
                confidence=1.0,
                scores={"neutral": 1.0},
            )

        if self._classifier is not None:
            try:
                return self._predict_with_transformers(cleaned_text)
            except Exception:
                # The heuristic fallback keeps the pipeline usable even if the
                # model backend is missing, misconfigured, or temporarily fails.
                pass

        return self._predict_with_heuristics(cleaned_text)

    def _build_transformers_pipeline(self):
        """Build a Hugging Face text-classification pipeline if possible."""
        if not self.config.model_name:
            return None

        try:
            from transformers import pipeline
        except Exception:
            return None

        return pipeline(
            task="text-classification",
            model=self.config.model_name,
            top_k=None,
        )

    def _predict_with_transformers(self, text: str) -> EmotionPrediction:
        """Run prediction through a transformers classifier."""
        raw_output = self._classifier(text)

        if raw_output and isinstance(raw_output, list) and isinstance(raw_output[0], list):
            raw_output = raw_output[0]

        scores = self._project_scores_from_model_output(raw_output)
        label, confidence = self._select_top_emotion(scores)

        return EmotionPrediction(
            label=label,
            confidence=confidence,
            scores=scores,
        )

    def _project_scores_from_model_output(self, raw_output: List[Dict[str, float]]) -> Dict[str, float]:
        """Map raw model labels to the smaller project taxonomy."""
        project_scores = self._empty_scores()

        for item in raw_output:
            raw_label = str(item.get("label", "")).strip().lower()
            raw_score = float(item.get("score", 0.0))

            project_label = self._map_model_label_to_project_label(raw_label)
            project_scores[project_label] += raw_score

        return self._normalize_scores(project_scores)

    def _map_model_label_to_project_label(self, raw_label: str) -> str:
        """Map external model labels into the project's five emotions."""
        label = raw_label.lower()

        if "sad" in label or "grief" in label or "depress" in label:
            return "sadness"
        if "ang" in label or "rage" in label or "annoy" in label:
            return "anger"
        if "fear" in label or "scared" in label or "terror" in label:
            return "fear"
        if "stress" in label or "anx" in label or "worry" in label or "nerv" in label:
            return "stress"
        if "neutral" in label or "calm" in label:
            return "neutral"

        # Unknown labels are treated as neutral to avoid over-flagging users.
        return "neutral"

    def _predict_with_heuristics(self, text: str) -> EmotionPrediction:
        """Use a transparent keyword-based fallback classifier.

        This is intentionally simple and explainable:
        each keyword match adds weight to one emotion, then scores are
        normalized to produce a distribution.

        The fallback is English-only because multilingual support is outside
        the scope of this project.
        """
        lowered_text = text.lower()
        scores = self._empty_scores()

        keyword_weights = {
            "sadness": {
                "sad": 1.0,
                "down": 0.7,
                "hopeless": 1.2,
                "cry": 1.1,
                "lonely": 1.0,
                "empty": 1.0,
                "depressed": 1.3,
            },
            "anger": {
                "angry": 1.0,
                "furious": 1.3,
                "annoyed": 0.8,
                "hate": 1.1,
                "mad": 0.9,
            },
            "fear": {
                "afraid": 1.0,
                "scared": 1.1,
                "terrified": 1.3,
                "fear": 1.0,
                "panic": 1.2,
                "frightened": 1.2,
            },
            "stress": {
                "stressed": 1.2,
                "stress": 1.0,
                "overwhelmed": 1.3,
                "pressure": 0.9,
                "anxious": 1.1,
                "worried": 0.9,
            },
        }

        for emotion, weights in keyword_weights.items():
            for keyword, weight in weights.items():
                if keyword in lowered_text:
                    scores[emotion] += weight

        scores = self._boost_scores_with_intensity_words(lowered_text, scores)
        scores = self._inject_neutral_score(scores)
        scores = self._normalize_scores(scores)

        label, confidence = self._select_top_emotion(scores)
        return EmotionPrediction(label=label, confidence=confidence, scores=scores)

    def _boost_scores_with_intensity_words(
        self,
        text: str,
        scores: Dict[str, float],
    ) -> Dict[str, float]:
        """Increase non-neutral scores when the message contains intensity cues."""
        boosted_scores = dict(scores)
        intensity_markers = (
            "very",
            "really",
            "extremely",
            "so much",
        )

        has_intensity = any(marker in text for marker in intensity_markers) or "!" in text

        if not has_intensity:
            return boosted_scores

        for emotion in ("sadness", "anger", "fear", "stress"):
            if boosted_scores[emotion] > 0.0:
                boosted_scores[emotion] *= 1.15

        return boosted_scores

    def _inject_neutral_score(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Assign a neutral score when no strong negative emotion is detected."""
        updated_scores = dict(scores)
        negative_total = (
            updated_scores["sadness"]
            + updated_scores["anger"]
            + updated_scores["fear"]
            + updated_scores["stress"]
        )

        if negative_total == 0.0:
            updated_scores["neutral"] = 1.0
        else:
            # Keep a small neutral mass so the output stays a full distribution.
            updated_scores["neutral"] = max(0.1, 1.0 - min(negative_total / 3.0, 0.9))

        return updated_scores

    def _select_top_emotion(self, scores: Dict[str, float]) -> (str, float):
        """Return the highest-scoring emotion and its confidence."""
        label = max(scores, key=scores.get)
        confidence = scores[label]
        return label, confidence

    def _normalize_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Normalize scores so they sum to 1."""
        total = sum(scores.values())

        if total <= 0.0:
            return {"neutral": 1.0, "sadness": 0.0, "anger": 0.0, "fear": 0.0, "stress": 0.0}

        return dict((emotion, value / total) for emotion, value in scores.items())

    def _empty_scores(self) -> Dict[str, float]:
        """Return an empty project-level score dictionary."""
        return dict((emotion, 0.0) for emotion in self.config.candidate_labels)
