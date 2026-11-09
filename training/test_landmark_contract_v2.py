"""Regression tests for the shared contract-v2 sequence rules."""

from __future__ import annotations

import unittest

import numpy as np

import landmark_contract_v2 as v2


def sequence_with_dominant_presence(length: int, indexes: list[int]) -> np.ndarray:
    features = np.zeros((length, v2.FRAME_FEATURES), dtype=np.float32)
    features[indexes, 66] = 1.0
    features[indexes, 63] = np.linspace(0.0, 1.0, len(indexes))
    return features


class ActiveIntervalTests(unittest.TestCase):
    def test_dense_real_run_beats_equal_span_intermittent_false_run(self) -> None:
        false_indexes = [0, 1, 2, 3, 4, 7, 8, 11, 14, 16, 17, 18]
        real_indexes = list(range(28, 47))
        features = sequence_with_dominant_presence(69, false_indexes + real_indexes)

        self.assertEqual(v2.active_interval(features), (26, 49))

    def test_context_is_bounded_by_sequence_edges(self) -> None:
        features = sequence_with_dominant_presence(8, [0, 1, 2])

        self.assertEqual(v2.active_interval(features), (0, 5))

    def test_sequence_without_dominant_hand_is_rejected(self) -> None:
        features = np.zeros((8, v2.FRAME_FEATURES), dtype=np.float32)

        with self.assertRaisesRegex(ValueError, "no detected dominant hand"):
            v2.active_interval(features)


if __name__ == "__main__":
    unittest.main()
