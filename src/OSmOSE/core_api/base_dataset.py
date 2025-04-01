"""BaseDataset: Base class for the Dataset objects.

Datasets are collections of Data, with methods
that simplify repeated operations on the data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Literal, TypeVar

from pandas import Timedelta, Timestamp, date_range
from soundfile import LibsndfileError

from OSmOSE.config import TIMESTAMP_FORMAT_EXPORTED_FILES
from OSmOSE.config import global_logging_context as glc
from OSmOSE.core_api.base_data import BaseData
from OSmOSE.core_api.base_file import BaseFile
from OSmOSE.core_api.event import Event
from OSmOSE.core_api.json_serializer import deserialize_json, serialize_json

if TYPE_CHECKING:
    from pathlib import Path

    import pytz

TData = TypeVar("TData", bound=BaseData)
TFile = TypeVar("TFile", bound=BaseFile)


class BaseDataset(Generic[TData, TFile], Event):
    """Base class for Dataset objects.

    Datasets are collections of Data, with methods
    that simplify repeated operations on the data.
    """

    def __init__(self, data: list[TData], name: str | None = None) -> None:
        """Instantiate a Dataset object from the Data objects."""
        self.data = data
        self._name = name
        self._has_default_name = name is None
        self._suffix = ""
        self._folder = None

    def __str__(self) -> str:
        """Overwrite __str__."""
        return self.name

    def __eq__(self, other: BaseDataset) -> bool:
        """Overwrite __eq__."""
        return sorted(self.data, key=lambda e: (e.begin, e.end)) == sorted(
            other.data,
            key=lambda e: (e.begin, e.end),
        )

    @property
    def name(self) -> str:
        """Name of the dataset."""
        base_name = (
            self.begin.strftime(TIMESTAMP_FORMAT_EXPORTED_FILES)
            if self._name is None
            else self._name
        )
        return base_name if not self.suffix else f"{base_name}_{self.suffix}"

    @name.setter
    def name(self, name: str | None) -> None:
        self._name = name

    @property
    def suffix(self) -> str:
        """Suffix that is applied to the name of the ads.

        This is used by the public API, for suffixing multiple core_api datasets
        that are created simultaneously and share the same namewith their specific type,
         e.g. _audio or _spectro.
        """
        return self._suffix

    @suffix.setter
    def suffix(self, suffix: str | None) -> None:
        self._suffix = suffix

    @property
    def has_default_name(self) -> bool:
        """Return True if the dataset has a default name, False if it has a given name."""
        return self._has_default_name

    @property
    def begin(self) -> Timestamp:
        """Begin of the first data object."""
        return min(data.begin for data in self.data)

    @property
    def end(self) -> Timestamp:
        """End of the last data object."""
        return max(data.end for data in self.data)

    @property
    def files(self) -> set[TFile]:
        """All files referred to by the Dataset."""
        return {file for data in self.data for file in data.files}

    @property
    def folder(self) -> Path:
        """Folder in which the dataset files are located."""
        return next(iter(file.path.parent for file in self.files), self._folder)

    @folder.setter
    def folder(self, folder: Path) -> None:
        """Move the dataset to the specified destination folder.

        Parameters
        ----------
        folder: Path
            The folder in which the dataset will be moved.
            It will be created if it does not exist.

        """
        self._folder = folder
        for file in self.files:
            file.move(folder)

    @property
    def data_duration(self) -> Timedelta:
        """Return the most frequent duration among durations of the data of this dataset, rounded to the nearest second."""
        data_durations = [
            Timedelta(data.duration).round(freq="1s") for data in self.data
        ]
        return max(set(data_durations), key=data_durations.count)

    def write(
        self,
        folder: Path,
        link: bool = False,
        first: int = 0,
        last: int | None = None,
    ) -> None:
        """Write all data objects in the specified folder.

        Parameters
        ----------
        folder: Path
            Folder in which to write the data.
        link: bool
            If True, the Data will be bound to the written file.
            Its items will be replaced with a single item, which will match the whole
            new File.
        first: int
            Index of the first data object to write.
        last: int | None
            Index after the last data object to write.

        """
        last = len(self.data) if last is None else last
        for data in self.data[first:last]:
            data.write(folder=folder, link=link)

    def to_dict(self) -> dict:
        """Serialize a BaseDataset to a dictionary.

        Returns
        -------
        dict:
            The serialized dictionary representing the BaseDataset.

        """
        return {"data": {str(d): d.to_dict() for d in self.data}, "name": self._name}

    @classmethod
    def from_dict(cls, dictionary: dict) -> BaseDataset:
        """Deserialize a BaseDataset from a dictionary.

        Parameters
        ----------
        dictionary: dict
            The serialized dictionary representing the BaseData.

        Returns
        -------
        AudioData
            The deserialized BaseDataset.

        """
        return cls(
            [BaseData.from_dict(d) for d in dictionary["data"].values()],
            name=dictionary["name"],
        )

    def write_json(self, folder: Path) -> None:
        """Write a serialized BaseDataset to a JSON file."""
        serialize_json(folder / f"{self.name}.json", self.to_dict())

    @classmethod
    def from_json(cls, file: Path) -> BaseDataset:
        """Deserialize a BaseDataset from a JSON file.

        Parameters
        ----------
        file: Path
            Path to the serialized JSON file representing the BaseDataset.

        Returns
        -------
        BaseDataset
            The deserialized BaseDataset.

        """
        return cls.from_dict(deserialize_json(file))

    @classmethod
    def from_files(  # noqa: PLR0913
        cls,
        files: list[TFile],
        begin: Timestamp | None = None,
        end: Timestamp | None = None,
        bound: Literal["files", "timedelta"] = "timedelta",
        data_duration: Timedelta | None = None,
        name: str | None = None,
    ) -> BaseDataset:
        """Return a base BaseDataset object from a list of Files.

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
        bound: Literal["files", "timedelta"]
            Bound between the original files and the dataset data.
            "files": one data will be created for each file.
            "timedelta": data objects of duration equal to data_duration will
            be created.
        data_duration: Timedelta | None
            Duration of the data objects.
            If bound is set to "files", this parameter has no effect.
            If provided, data will be evenly distributed between begin and end.
            Else, one data object will cover the whole time period.
        name: str|None
            Name of the dataset.

        Returns
        -------
        BaseDataset[TItem, TFile]:
        The DataBase object.

        """
        if bound == "files":
            data_base = [BaseData.from_files([f]) for f in files]
            data_base = BaseData.remove_overlaps(data_base)
            return cls(data=data_base, name=name)

        if not begin:
            begin = min(file.begin for file in files)
        if not end:
            end = max(file.end for file in files)
        if data_duration:
            data_base = [
                BaseData.from_files(files, begin=b, end=b + data_duration)
                for b in date_range(begin, end, freq=data_duration, inclusive="left")
            ]
        else:
            data_base = [BaseData.from_files(files, begin=begin, end=end)]
        return cls(data_base, name=name)

    @classmethod
    def from_folder(  # noqa: PLR0913
        cls,
        folder: Path,
        strptime_format: str,
        file_class: type[TFile] = BaseFile,
        supported_file_extensions: list[str] | None = None,
        begin: Timestamp | None = None,
        end: Timestamp | None = None,
        timezone: str | pytz.timezone | None = None,
        bound: Literal["files", "timedelta"] = "timedelta",
        data_duration: Timedelta | None = None,
        name: str | None = None,
    ) -> BaseDataset:
        """Return a BaseDataset from a folder containing the base files.

        Parameters
        ----------
        folder: Path
            The folder containing the files.
        strptime_format: str
            The strptime format of the timestamps in the file names.
        file_class: type[Tfile]
            Derived type of BaseFile used to instantiate the dataset.
        supported_file_extensions: list[str]
            List of supported file extensions for parsing TFiles.
        begin: Timestamp | None
            The begin of the dataset.
            Defaulted to the begin of the first file.
        end: Timestamp | None
            The end of the dataset.
            Defaulted to the end of the last file.
        timezone: str | pytz.timezone | None
            The timezone in which the file should be localized.
            If None, the file begin/end will be tz-naive.
            If different from a timezone parsed from the filename, the timestamps'
            timezone will be converted from the parsed timezone
            to the specified timezone.
        bound: Literal["files", "timedelta"]
            Bound between the original files and the dataset data.
            "files": one data will be created for each file.
            "timedelta": data objects of duration equal to data_duration will
            be created.
        data_duration: Timedelta | None
            Duration of the data objects.
            If bound is set to "files", this parameter has no effect.
            If provided, data will be evenly distributed between begin and end.
            Else, one object will cover the whole time period.
        name: str|None
            Name of the dataset.

        Returns
        -------
        Basedataset:
            The base dataset.

        """
        if supported_file_extensions is None:
            supported_file_extensions = []
        valid_files = []
        rejected_files = []
        for file in folder.iterdir():
            if file.suffix.lower() not in supported_file_extensions:
                continue
            try:
                f = file_class(file, strptime_format=strptime_format, timezone=timezone)
                valid_files.append(f)
            except (ValueError, LibsndfileError):
                rejected_files.append(file)

        if rejected_files:
            rejected_files = "\n\t".join(f.name for f in rejected_files)
            glc.logger.warn(
                f"The following files couldn't be parsed:\n\t{rejected_files}",
            )

        if not valid_files:
            raise FileNotFoundError(f"No valid file found in {folder}.")

        return BaseDataset.from_files(
            files=valid_files,
            begin=begin,
            end=end,
            bound=bound,
            data_duration=data_duration,
            name=name,
        )
