"""Custom frequency scales for plotting spectrograms.

The custom scale is formed from a list of ScaleParts, which assign a
frequency range to a range on the scale.
Provided ScaleParts should cover the whole scale (from 0% to 100%).

Such Scale can then be passed to the SpectroData.plot() method for the
spectrogram to be plotted on a custom frequency scale.

"""

from __future__ import annotations

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

    def __eq__(self, other: any) -> bool:
        """Overwrite eq dunder."""
        if type(other) is not ScalePart:
            return False
        return (
            self.p_min == other.p_min
            and self.p_max == other.p_max
            and self.f_min == other.f_min
            and self.f_max == other.f_max
        )


class Scale:
    """Class that represent a custom frequency scale for plotting spectrograms.

    The custom scale is formed from a list of ScaleParts, which assign a
    frequency range to a range on the scale.
    Provided ScaleParts should cover the whole scale (from 0% to 100%).

    Such Scale can then be passed to the SpectroData.plot() method for the
    spectrogram to be plotted on a custom frequency scale.

    """

    def __init__(self, parts: list[ScalePart]) -> None:
        """Initialize a Scale object."""
        self.parts = sorted(parts, key=lambda p: (p.p_min, p.p_max))

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
            v for scale in self.parts for v in scale.get_values(original_scale_length)
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

    def get_mapped_values(self, original_scale: list[float]) -> list[float]:
        """Return the closest values of the mapped scale from the original scale.

        Parameters
        ----------
        original_scale: list[float]
            Original scale from which the mapped scale is computed.

        Returns
        -------
        list[float]
            Values from the original scale that are the closest to the mapped scale.

        """
        return [original_scale[i] for i in self.get_mapped_indexes(original_scale)]

    def rescale(
        self,
        sx_matrix: np.ndarray,
        original_scale: np.ndarray | list,
    ) -> np.ndarray:
        """Rescale the given spectrum matrix according to the present scale.

        Parameters
        ----------
        sx_matrix: np.ndarray
            Spectrum matrix.
        original_scale: np.ndarray
            Original frequency axis of the spectrum matrix.

        Returns
        -------
        np.ndarray
            Spectrum matrix mapped on the present scale.

        """
        if type(original_scale) is np.ndarray:
            original_scale = original_scale.tolist()

        new_scale_indexes = self.get_mapped_indexes(original_scale)

        return sx_matrix[new_scale_indexes]

    def to_dict_value(self) -> list[list]:
        """Serialize a Scale to a dictionary entry."""
        return [[part.p_min, part.p_max, part.f_min, part.f_max] for part in self.parts]

    @classmethod
    def from_dict_value(cls, dict_value: list[list]) -> Scale:
        """Deserialize a Scale from a dictionary entry."""
        return cls([ScalePart(*scale) for scale in dict_value])

    def __eq__(self, other: any) -> bool:
        """Overwrite eq dunder."""
        if type(other) is not Scale:
            return False
        return self.parts == other.parts
