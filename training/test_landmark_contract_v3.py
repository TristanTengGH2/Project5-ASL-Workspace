"""Regression tests for aspect-correct landmark contract v3."""

from __future__ import annotations

import unittest

import numpy as np

import landmark_contract_v3 as v3


def normalized(points: np.ndarray, width: int, height: int) -> np.ndarray:
    result = points.astype(np.float32, copy=True)
    result[:, 0] /= width
    result[:, 1] /= height
    result[:, 2] /= width
    return result


class AspectCorrectionTests(unittest.TestCase):
    def test_same_pixel_geometry_matches_across_aspect_ratios(self) -> None:
        hand = np.array(
            [[400 + index * 3, 300 + index * 2, -index] for index in range(21)],
            dtype=np.float32,
        )
        pose = np.array(
            [[500 + index, 250 + index, 0] for index in range(33)], dtype=np.float32
        )
        pose[0] = [500, 180, 0]
        pose[11] = [400, 400, 0]
        pose[12] = [600, 400, 0]
        present = np.ones(33, dtype=bool)
        portrait = v3.frame_features(
            None, normalized(hand, 1000, 1600), normalized(pose, 1000, 1600), present, 1000, 1600
        )
        landscape = v3.frame_features(
            None, normalized(hand, 1600, 1000), normalized(pose, 1600, 1000), present, 1600, 1000
        )
        np.testing.assert_allclose(portrait, landscape, atol=1e-6)

    def test_head_offset_is_explicit(self) -> None:
        hand = np.array([[400 + index, 300 + index, 0] for index in range(21)], dtype=np.float32)
        pose = np.zeros((33, 3), dtype=np.float32)
        pose[0] = [500, 200, 0]
        pose[11] = [400, 400, 0]
        pose[12] = [600, 400, 0]
        present = np.ones(33, dtype=bool)
        features = v3.frame_features(None, normalized(hand, 1000, 1000), normalized(pose, 1000, 1000), present, 1000, 1000)
        np.testing.assert_allclose(features[v3.HAND_FEATURES + 66 : v3.HAND_FEATURES + 68], [-0.5, 0.5])
        self.assertEqual(features[v3.HAND_FEATURES + v3.PRESENCE_INDEX], 1)


if __name__ == "__main__":
    unittest.main()
