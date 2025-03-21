"""BaseData: Base class for the Data objects.

Data corresponds to data scattered through different Files.
The data is accessed via an Item object per File.
"""

from __future__ import annotations

from pathlib import Path
from typing import Generic, TypeVar

import numpy as np
from pandas import Timestamp, date_range, to_datetime

from OSmOSE.config import (
    DPDEFAULT,
    TIMESTAMP_FORMAT_AUDIO_FILE,
    TIMESTAMP_FORMAT_EXPORTED_FILES,
)
from OSmOSE.core_api.base_file import BaseFile
from OSmOSE.core_api.base_item import BaseItem
from OSmOSE.core_api.event import Event

TItem = TypeVar("TItem", bound=BaseItem)
TFile = TypeVar("TFile", bound=BaseFile)


class BaseData(Generic[TItem, TFile], Event):
    """Base class for the Data objects.

    Data corresponds to data scattered through different Files.
    The data is accessed via an Item object per File.
    """

    def __init__(
        self,
        items: list[TItem] | None = None,
        begin: Timestamp | None = None,
        end: Timestamp | None = None,
    ) -> None:
        """Initialize a BaseData from a list of Items.

        Parameters
        ----------
        items: list[BaseItem] | None
            List of the Items constituting the Data.
            Defaulted to an empty item ranging from begin to end.
        begin: Timestamp | None
            Only effective if items is None.
            Set the begin of the empty data.
        end: Timestamp | None
            Only effective if items is None.
            Set the end of the empty data.

        """
        if not items:
            items = [BaseItem(begin=begin, end=end)]
        self.items = items
        self.begin = min(item.begin for item in self.items)
        self.end = max(item.end for item in self.items)

    @property
    def is_empty(self) -> bool:
        """Return true if every item of this data object is empty."""
        return all(item.is_empty for item in self.items)

    def get_value(self) -> np.ndarray:
        """Get the concatenated values from all Items."""
        return np.concatenate([item.get_value() for item in self.items])

    @staticmethod
    def create_directories(path: Path) -> None:
        """Create the directory in which the data will be written.

        The actual data writing is left to the specified classes.
        """
        path.mkdir(parents=True, exist_ok=True, mode=DPDEFAULT)

    def write(self, folder: Path) -> None:
        """Abstract method for writing data to file."""

    def to_dict(self) -> dict:
        """Serialize a BaseData to a dictionary.

        Returns
        -------
        dict:
            The serialized dictionary representing the BaseData.

        """
        return {
            "begin": self.begin.strftime(TIMESTAMP_FORMAT_AUDIO_FILE),
            "end": self.end.strftime(TIMESTAMP_FORMAT_AUDIO_FILE),
            "files": {str(f): f.to_dict() for f in self.files},
        }

    @classmethod
    def from_dict(cls, dictionary: dict) -> BaseData:
        """Deserialize a BaseData from a dictionary.

        Parameters
        ----------
        dictionary: dict
            The serialized dictionary representing the BaseData.

        Returns
        -------
        AudioData
            The deserialized BaseData.

        """
        files = [
            BaseFile(
                Path(file["path"]),
                begin=to_datetime(
                    file["begin"],
                    format=TIMESTAMP_FORMAT_EXPORTED_FILES,
                ),
                end=to_datetime(file["end"], format=TIMESTAMP_FORMAT_EXPORTED_FILES),
            )
            for file in dictionary["files"].values()
        ]
        begin = Timestamp(dictionary["begin"])
        end = Timestamp(dictionary["end"])
        return cls.from_files(files, begin, end)

    @property
    def files(self) -> set[TFile]:
        """All files referred to by the Data."""
        return {item.file for item in self.items if item.file is not None}

    def split(self, nb_subdata: int = 2) -> list[BaseData]:
        """Split the data object in the specified number of subdata.

        Parameters
        ----------
        nb_subdata: int
            Number of subdata in which to split the data.

        Returns
        -------
        list[BaseData]
            The list of BaseData subdata objects.

        """
        dates = date_range(self.begin, self.end, periods=nb_subdata + 1)
        subdata_dates = zip(dates, dates[1:])
        return [
            BaseData.from_files(files=list(self.files), begin=b, end=e)
            for b, e in subdata_dates
        ]

    @classmethod
    def from_files(
        cls,
        files: list[TFile],
        begin: Timestamp | None = None,
        end: Timestamp | None = None,
    ) -> BaseData[TItem, TFile]:
        """Return a base DataBase object from a list of Files.

        Parameters
        ----------
        files: list[TFile]
            List of Files containing the data.
        begin: Timestamp | None
            Begin of the data object.
            Defaulted to the begin of the first file.
        end: Timestamp | None
            End of the data object.
            Defaulted to the end of the last file.

        Returns
        -------
        BaseData[TItem, TFile]:
        The BaseData object.

        """
        items = cls.items_from_files(files, begin, end)
        return cls(items)

    @classmethod
    def items_from_files(
        cls,
        files: list[TFile],
        begin: Timestamp | None = None,
        end: Timestamp | None = None,
    ) -> list[BaseItem]:
        """Return a list of Items from a list of Files and timestamps.

        The Items range from begin to end.
        They point to the files that match their timestamps.

        Parameters
        ----------
        files: list[TFile]
            The Files encapsulated in the Data object.
        begin: pandas.Timestamp | None
            The begin of the Data object.
            defaulted to the begin of the first File.
        end: pandas.Timestamp | None
            The end of the Data object.
            defaulted to the end of the last File.

        Returns
        -------
        list[BaseItem]
            The list of Items that point to the files.

        """
        begin = min(file.begin for file in files) if begin is None else begin
        end = max(file.end for file in files) if end is None else end

        included_files = [
            file for file in files if file.overlaps(Event(begin=begin, end=end))
        ]

        items = [BaseItem(file, begin, end) for file in included_files]
        if not items:
            items.append(BaseItem(begin=begin, end=end))
        if (first_item := sorted(items, key=lambda item: item.begin)[0]).begin > begin:
            items.append(BaseItem(begin=begin, end=first_item.begin))
        if (last_item := sorted(items, key=lambda item: item.end)[-1]).end < end:
            items.append(BaseItem(begin=last_item.end, end=end))
        items = Event.remove_overlaps(items)
        return Event.fill_gaps(items, BaseItem)
