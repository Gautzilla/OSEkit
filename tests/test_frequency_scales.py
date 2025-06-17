import pytest

from OSmOSE.core_api.frequency_scale import ScalePart


@pytest.mark.parametrize(
    ("scale_part", "nb_points", "expected"),
    [
        pytest.param(
            ScalePart(
                p_min=0,
                p_max=100,
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
                p_max=100,
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
    scale_part: ScalePart, nb_points: int, expected: list[int]
) -> None:
    assert list(scale_part.get_frequencies(nb_points)) == expected
