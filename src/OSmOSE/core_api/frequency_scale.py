from dataclasses import dataclass

import numpy as np

from OSmOSE.utils.core_utils import get_closest_value_index


@dataclass
class ScalePart:
    """Represent a part of the frequency scale of a spectrogram.

    The given part goes from:
    p_min (in % of the axis), representing f_min
    to:
    p_max (in % of the axis), representing f_max
    """

    p_min: float
    p_max: float
    f_min: float
    f_max: float

    def get_frequencies(self, nb_points: int) -> list[int]:
        """Return the frequency points of the present scale part."""
        return list(map(round, np.linspace(self.f_min, self.f_max, nb_points)))

    def get_indexes(self, scale_length: int) -> tuple[int, int]:
        """Return the indexes of the present scale part in the full scale."""
        return int(self.p_min * scale_length), int(self.p_max * scale_length)

    def get_values(self, scale_length: int) -> list[int]:
        """Return the values of the present scale part in the full scale."""
        start, stop = self.get_indexes(scale_length)
        return list(map(round, np.linspace(self.f_min, self.f_max, stop - start)))


class Scale:
    def __init__(self, parts: list[ScalePart]):
        self.parts = parts

    def map(self, original_scale_length: int) -> list[float]:
        """Map a given scale to the custom scale defined by its ScaleParts.

        Parameters
        ----------
        original_scale_length: int
            Length of the original frequency scale.

        Returns
        -------
        list[float]
            Mapped frequency scale.
            Each ScalePart from the Scale.parts attribute are concatenated
            to form the returned scale.

        """
        return [
            v
            for scale in sorted(self.parts, key=lambda p: (p.p_min, p.p_max))
            for v in scale.get_values(original_scale_length)
        ]

    def get_mapped_indexes(self, original_scale: list[float]) -> list[int]:
        """Return the indexes of the present scale in the original scale.

        The indexes are those of the closest value from the mapped values
        in the original scale.

        Parameters
        ----------
        original_scale: list[float]
            Original scale from which the mapped scale is computed.

        Returns
        -------
        list[int]
            Indexes of the closest value from the mapped values in the
            original scale.

        """
        mapped_scale = self.map(len(original_scale))
        return [
            get_closest_value_index(mapped, original_scale) for mapped in mapped_scale
        ]
