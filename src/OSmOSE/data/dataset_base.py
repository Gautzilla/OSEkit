from __future__ import annotations

from typing import Generic, TypeVar

from pandas import Timedelta, Timestamp, date_range

from OSmOSE.data.data_base import DataBase
from OSmOSE.data.file_base import FileBase

TData = TypeVar("TData", bound=DataBase)
TFile = TypeVar("TFile", bound=FileBase)


class DatasetBase(Generic[TData, TFile]):
    """Base class for Dataset objects.

    Datasets are collections of Data, with methods
    that simplify repeated operations on the data.
    """

    def __init__(self, data: list[TData]) -> None:
        """Instantiate a Dataset object from the Data objects."""
        self.data = data

    @property
    def begin(self) -> Timestamp:
        """Begin of the first data object."""
        return min(data.begin for data in self.data)

    @property
    def end(self) -> Timestamp:
        """End of the last data object."""
        return max(data.end for data in self.data)

    @classmethod
    def from_files(
        cls,
        files: list[TFile],
        begin: Timestamp | None = None,
        end: Timestamp | None = None,
        data_duration: Timedelta | None = None,
    ) -> DatasetBase:
        """Return a base DatasetBase object from a list of Files.

        Parameters
        ----------
        files: list[TFile]
            The list of files contained in the Dataset.
        begin: Timestamp | None
            Begin of the first data object.
            Defaulted to the begin of the first file.
        end: Timestamp | None
            End of the last data object.
            Defaulted to the end of the last file.
        data_duration: Timedelta | None
            Duration of the data objects.
            If provided, data will be evenly distributed between begin and end.
            Else, one data object will cover the whole time period.

        Returns
        -------
        DataBase[TItem, TFile]:
        The DataBase object.

        """
        if not begin:
            begin = min(file.begin for file in files)
        if not end:
            end = max(file.end for file in files)
        if data_duration:
            data_base = [
                DataBase.from_files(files, begin=b, end=b + data_duration)
                for b in date_range(begin, end, freq=data_duration)[:-1]
            ]
        else:
            data_base = [DataBase.from_files(files, begin=begin, end=end)]
        return cls(data_base)
