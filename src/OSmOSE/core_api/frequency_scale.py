from dataclasses import dataclass

import numpy as np


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
