"""Unit tests for the affective pipeline."""

import unittest

from beyond_persuasion.affective.pipeline import EmotionAnalyzer, EmotionAnalyzerConfig


class EmotionAnalyzerUnitTests(unittest.TestCase):
    """Verify label mapping and score projection behavior."""

    def setUp(self) -> None:
        self.analyzer = EmotionAnalyzer(
            EmotionAnalyzerConfig(
                model_name=None,
                use_transformers=False,
            )
        )

    def test_project_scores_ignore_unrelated_positive_labels(self) -> None:
        """Unrelated labels should not erase a vulnerable signal."""
        raw_output = [
            {"label": "desire", "score": 0.60},
            {"label": "approval", "score": 0.15},
            {"label": "nervousness", "score": 0.20},
            {"label": "fear", "score": 0.05},
        ]

        scores = self.analyzer._project_scores_from_model_output(raw_output)

        self.assertAlmostEqual(0.80, scores["stress"], places=2)
        self.assertAlmostEqual(0.20, scores["fear"], places=2)
        self.assertAlmostEqual(0.0, scores["neutral"], places=3)

    def test_project_scores_fall_back_to_neutral_when_no_label_matches(self) -> None:
        """If no project label is recognized, the result should be neutral."""
        raw_output = [
            {"label": "desire", "score": 0.70},
            {"label": "optimism", "score": 0.20},
            {"label": "approval", "score": 0.10},
        ]

        scores = self.analyzer._project_scores_from_model_output(raw_output)

        self.assertEqual("neutral", max(scores, key=scores.get))
        self.assertAlmostEqual(1.0, scores["neutral"], places=3)

    def test_mapping_covers_project_relevant_go_emotions_labels(self) -> None:
        """Important GoEmotions labels should map to the project taxonomy."""
        self.assertEqual("stress", self.analyzer._map_model_label_to_project_label("nervousness"))
        self.assertEqual("sadness", self.analyzer._map_model_label_to_project_label("disappointment"))
        self.assertEqual("anger", self.analyzer._map_model_label_to_project_label("disgust"))


if __name__ == "__main__":
    unittest.main()
