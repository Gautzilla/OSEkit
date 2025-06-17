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
