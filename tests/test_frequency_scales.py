import numpy as np
import pytest

from OSmOSE.core_api.frequency_scale import Scale, ScalePart


@pytest.mark.parametrize(
    ("scale_part", "nb_points", "expected"),
    [
        pytest.param(
            ScalePart(
                p_min=0,
                p_max=1.0,
                f_min=0,
                f_max=3,
            ),
            4,
            [0, 1, 2, 3],
            id="simple_case",
        ),
        pytest.param(
            ScalePart(
                p_min=0,
                p_max=1.0,
                f_min=10,
                f_max=12,
            ),
            6,
            [10, 10, 11, 11, 12, 12],
            id="float_frequencies_are_rounded",
        ),
    ],
)
def test_frequency_scale_part_get_frequencies(
    scale_part: ScalePart,
    nb_points: int,
    expected: list[int],
) -> None:
    assert list(scale_part.get_frequencies(nb_points)) == expected


@pytest.mark.parametrize(
    ("scale_part", "scale_length", "expected"),
    [
        pytest.param(
            ScalePart(
                p_min=0,
                p_max=1.0,
                f_min=0,
                f_max=500,
            ),
            10,
            (0, 10),
            id="full_scale",
        ),
        pytest.param(
            ScalePart(
                p_min=0,
                p_max=0.5,
                f_min=0,
                f_max=500,
            ),
            10,
            (0, 5),
            id="first_half",
        ),
        pytest.param(
            ScalePart(
                p_min=0.5,
                p_max=1.0,
                f_min=0,
                f_max=500,
            ),
            10,
            (5, 10),
            id="last_half",
        ),
        pytest.param(
            ScalePart(
                p_min=0.18,
                p_max=0.38,
                f_min=0,
                f_max=500,
            ),
            10,
            (1, 3),
            id="float_index_to_floor",
        ),
    ],
)
def test_frequency_scale_part_get_indexes(
    scale_part: ScalePart,
    scale_length: int,
    expected: list[int],
) -> None:
    assert scale_part.get_indexes(scale_length) == expected


@pytest.mark.parametrize(
    ("scale_part", "nb_points", "expected"),
    [
        pytest.param(
            ScalePart(
                p_min=0,
                p_max=1.0,
                f_min=0,
                f_max=3,
            ),
            4,
            [0, 1, 2, 3],
            id="full_scale",
        ),
        pytest.param(
            ScalePart(
                p_min=0,
                p_max=1.0,
                f_min=100,
                f_max=200,
            ),
            5,
            [100, 125, 150, 175, 200],
            id="full_scale_large_frequencies",
        ),
        pytest.param(
            ScalePart(
                p_min=0.0,
                p_max=0.5,
                f_min=100,
                f_max=200,
            ),
            5,
            [100, 200],
            id="odd_first_half",
        ),
        pytest.param(
            ScalePart(
                p_min=0.5,
                p_max=1.0,
                f_min=200,
                f_max=300,
            ),
            5,
            [200, 250, 300],
            id="odd_second_half",
        ),
    ],
)
def test_frequency_scale_part_get_values(
    scale_part: ScalePart,
    nb_points: int,
    expected: list[int],
) -> None:
    assert scale_part.get_values(nb_points) == expected


@pytest.mark.parametrize(
    ("scale", "scale_length", "expected"),
    [
        pytest.param(
            Scale(
                parts=[
                    ScalePart(
                        p_min=0,
                        p_max=1.0,
                        f_min=0,
                        f_max=3,
                    ),
                ],
            ),
            4,
            [0, 1, 2, 3],
            id="one_full_part",
        ),
        pytest.param(
            Scale(
                parts=[
                    ScalePart(
                        p_min=0,
                        p_max=0.5,
                        f_min=0,
                        f_max=1,
                    ),
                    ScalePart(
                        p_min=0.5,
                        p_max=1.0,
                        f_min=2,
                        f_max=3,
                    ),
                ],
            ),
            4,
            [0, 1, 2, 3],
            id="even_length_cut_in_half",
        ),
        pytest.param(
            Scale(
                parts=[
                    ScalePart(
                        p_min=0,
                        p_max=0.5,
                        f_min=0,
                        f_max=1,
                    ),
                    ScalePart(
                        p_min=0.5,
                        p_max=1.0,
                        f_min=2,
                        f_max=4,
                    ),
                ],
            ),
            5,
            [0, 1, 2, 3, 4],
            id="odd_length_cut_in_half",
        ),
        pytest.param(
            Scale(
                parts=[
                    ScalePart(
                        p_min=0,
                        p_max=0.1,
                        f_min=100,
                        f_max=200,
                    ),
                    ScalePart(
                        p_min=0.1,
                        p_max=0.5,
                        f_min=500,
                        f_max=1_200,
                    ),
                    ScalePart(
                        p_min=0.5,
                        p_max=1.0,
                        f_min=3_100,
                        f_max=4_000,
                    ),
                ],
            ),
            20,
            [
                100,
                200,
                500,
                600,
                700,
                800,
                900,
                1_000,
                1_100,
                1_200,
                3_100,
                3_200,
                3_300,
                3_400,
                3_500,
                3_600,
                3_700,
                3_800,
                3_900,
                4_000,
            ],
            id="non_consecutive_parts",
        ),
    ],
)
def test_frequency_scale_map(
    scale: Scale,
    scale_length: int,
    expected: list[float],
) -> None:
    assert scale.map(scale_length) == expected


@pytest.mark.parametrize(
    ("scale", "original_scale", "expected"),
    [
        pytest.param(
            Scale(
                parts=[
                    ScalePart(p_min=0.0, p_max=1.0, f_min=0, f_max=5.0),
                ],
            ),
            [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
            [0, 1, 2, 3, 4, 5],
            id="same_scale",
        ),
        pytest.param(
            Scale(
                parts=[
                    ScalePart(p_min=0.0, p_max=0.5, f_min=0, f_max=2.0),
                    ScalePart(p_min=0.5, p_max=1.0, f_min=3.0, f_max=5.0),
                ],
            ),
            [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
            [0, 1, 2, 3, 4, 5],
            id="same_scale_in_two_parts",
        ),
        pytest.param(
            Scale(
                parts=[
                    ScalePart(p_min=0.0, p_max=0.8, f_min=0, f_max=1.0),
                    ScalePart(p_min=0.8, p_max=1.0, f_min=8.0, f_max=9.0),
                ],
            ),
            [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0],
            [0, 0, 0, 0, 1, 1, 1, 1, 8, 9],
            id="two_different_parts",
        ),
        pytest.param(
            Scale(
                parts=[
                    ScalePart(p_min=0.0, p_max=0.8, f_min=100, f_max=110.0),
                    ScalePart(p_min=0.8, p_max=1.0, f_min=180.0, f_max=190.0),
                ],
            ),
            [100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 160.0, 170.0, 180.0, 190.0],
            [0, 0, 0, 0, 1, 1, 1, 1, 8, 9],
            id="different_frequencies_same_indexes",
        ),
    ],
)
def test_frequency_scale_mapped_indexes(
    scale: Scale,
    original_scale: list[float],
    expected: list[int],
) -> None:
    assert scale.get_mapped_indexes(original_scale=original_scale) == expected


@pytest.mark.parametrize(
    ("scale", "original_scale", "expected"),
    [
        pytest.param(
            Scale(
                parts=[
                    ScalePart(p_min=0.0, p_max=1.0, f_min=0, f_max=5.0),
                ],
            ),
            [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
            [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
            id="same_scale",
        ),
        pytest.param(
            Scale(
                parts=[
                    ScalePart(p_min=0.0, p_max=0.5, f_min=0, f_max=2.0),
                    ScalePart(p_min=0.5, p_max=1.0, f_min=3.0, f_max=5.0),
                ],
            ),
            [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
            [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
            id="same_scale_in_two_parts",
        ),
        pytest.param(
            Scale(
                parts=[
                    ScalePart(p_min=0.0, p_max=0.8, f_min=0, f_max=1.0),
                    ScalePart(p_min=0.8, p_max=1.0, f_min=8.0, f_max=9.0),
                ],
            ),
            [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0],
            [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 8.0, 9.0],
            id="two_different_parts",
        ),
        pytest.param(
            Scale(
                parts=[
                    ScalePart(p_min=0.0, p_max=0.8, f_min=100, f_max=110.0),
                    ScalePart(p_min=0.8, p_max=1.0, f_min=180.0, f_max=190.0),
                ],
            ),
            [100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 160.0, 170.0, 180.0, 190.0],
            [100.0, 100.0, 100.0, 100.0, 110.0, 110.0, 110.0, 110.0, 180.0, 190.0],
            id="different_frequencies_same_indexes",
        ),
    ],
)
def test_frequency_scale_mapped_values(
    scale: Scale,
    original_scale: list[float],
    expected: list[int],
) -> None:
    assert scale.get_mapped_values(original_scale=original_scale) == expected


@pytest.mark.parametrize(
    ("input_matrix", "original_scale", "scale", "expected_matrix"),
    [
        pytest.param(
            np.array([[1, 10, 100], [2, 20, 200], [3, 30, 300], [4, 40, 400]]),
            [0.0, 1.0, 2.0, 3.0],
            Scale([ScalePart(0.0, 1.0, 0.0, 3.0)]),
            np.array([[1, 10, 100], [2, 20, 200], [3, 30, 300], [4, 40, 400]]),
            id="same_scale",
        ),
        pytest.param(
            np.array([[1, 10, 100], [2, 20, 200], [3, 30, 300], [4, 40, 400]]),
            [0.0, 1.0, 2.0, 3.0],
            Scale([ScalePart(0.0, 0.5, 0.0, 1.0), ScalePart(0.5, 1.0, 0.0, 1.0)]),
            np.array([[1, 10, 100], [2, 20, 200], [1, 10, 100], [2, 20, 200]]),
            id="repeat_first_half",
        ),
        pytest.param(
            np.array([[1, 10, 100], [2, 20, 200], [3, 30, 300], [4, 40, 400]]),
            [0.0, 1.0, 2.0, 3.0],
            Scale([ScalePart(0.0, 0.5, 2.0, 3.0), ScalePart(0.5, 1.0, 0.0, 1.0)]),
            np.array([[3, 30, 300], [4, 40, 400], [1, 10, 100], [2, 20, 200]]),
            id="switch_halves",
        ),
        pytest.param(
            np.array([[1, 10, 100], [2, 20, 200], [3, 30, 300], [4, 40, 400]]),
            [0.0, 1.0, 2.0, 3.0],
            Scale(
                [
                    ScalePart(0.0, 0.25, 3.0, 4.0),
                    ScalePart(0.25, 0.5, 2.0, 3.0),
                    ScalePart(0.5, 0.75, 0.0, 1.0),
                    ScalePart(0.75, 1.0, 1.0, 2.0),
                ],
            ),
            np.array([[4, 40, 400], [3, 30, 300], [1, 10, 100], [2, 20, 200]]),
            id="four_parts",
        ),
    ],
)
def test_frequency_scale_rescale(
    input_matrix: np.ndarray,
    original_scale: np.ndarray,
    scale: Scale,
    expected_matrix: np.ndarray,
) -> None:
    scaled_matrix = scale.rescale(input_matrix, original_scale)
    assert np.array_equal(scaled_matrix, expected_matrix)
