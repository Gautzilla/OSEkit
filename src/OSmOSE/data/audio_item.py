"""AudioItem corresponding to a portion of an AudioFile object."""

from __future__ import annotations

from typing import TYPE_CHECKING

from OSmOSE.data.audio_file import AudioFile
from OSmOSE.data.base_file import BaseFile
from OSmOSE.data.base_item import BaseItem

if TYPE_CHECKING:
    import numpy as np
    from pandas import Timestamp


class AudioItem(BaseItem[AudioFile]):
    """AudioItem corresponding to a portion of an AudioFile object."""

    def __init__(
        self,
        file: AudioFile | None = None,
        begin: Timestamp | None = None,
        end: Timestamp | None = None,
    ) -> None:
        """Initialize an AudioItem from an AudioFile and begin/end timestamps.

        Parameters
        ----------
        file: OSmOSE.data.audio_file.AudioFile
            The AudioFile in which this Item belongs.
        begin: pandas.Timestamp (optional)
            The timestamp at which this item begins.
            It is defaulted to the AudioFile begin.
        end: pandas.Timestamp (optional)
            The timestamp at which this item ends.
            It is defaulted to the AudioFile end.

        """
        super().__init__(file, begin, end)

    @property
    def sample_rate(self) -> float:
        """Sample rate of the associated AudioFile."""
        return None if self.is_empty else self.file.metadata.samplerate

    @property
    def nb_channels(self) -> int:
        """Number of channels in the associated AudioFile."""
        return 0 if self.is_empty else self.file.metadata.channels

    @property
    def shape(self) -> int:
        """Number of points in the audio item data."""
        return round(self.sample_rate * self.duration.total_seconds())

    def get_value(self) -> np.ndarray:
        """Get the values from the File between the begin and stop timestamps.

        If the Item is empty, return a single 0.
        """
        return super().get_value()[:self.shape]

    @classmethod
    def from_base_item(cls, item: BaseItem) -> AudioItem:
        """Return an AudioItem object from a BaseItem object."""
        file = item.file
        if not file or isinstance(file, AudioFile):
            return cls(file=file, begin=item.begin, end=item.end)
        if isinstance(file, BaseFile):
            return cls(
                file=AudioFile.from_base_file(file),
                begin=item.begin,
                end=item.end,
            )
        raise TypeError
