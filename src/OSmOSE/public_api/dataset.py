from __future__ import annotations

import shutil
from pathlib import Path
from typing import TypeVar

from OSmOSE.core_api.audio_dataset import AudioDataset
from OSmOSE.core_api.spectro_dataset import SpectroDataset


class Dataset:
    """Main class of the Public API.

    The Dataset correspond to a collection of audio, spectro and auxilary core_api datasets.
    It has additionnal metadata that can be exported, e.g. to APLOSE.

    """

    def __init__(
        self,
        folder: Path,
        strptime_format: str,
        gps_coordinates: str | list | tuple = (0, 0),
        depth: str | int = 0,
        timezone: str | None = None,
    ) -> None:
        """Initialize a Dataset."""
        self.folder = folder
        self.strptime_format = strptime_format
        self.gps_coordinates = gps_coordinates
        self.depth = depth
        self.timezone = timezone
        self.datasets = {}

    def build(self) -> None:
        """Build the Dataset.

        Building a dataset moves the original audio files to a specific folder
        and creates metadata csv used by APLOSE.

        """
        ads = AudioDataset.from_folder(
            self.folder,
            strptime_format=self.strptime_format,
        )
        self.datasets["original"] = ads
        self._sort_data(self.datasets["original"])

    def reset(self) -> None:
        """Reset the Dataset.

        Resetting a dataset will move back the original audio files and the content of the "other" folder
         to the root folder.
        WARNING: all other files and folders will be deleted.
        """
        files_to_remove = list(self.folder.iterdir())
        self.datasets["original"].move(self.folder)
        for file in files_to_remove:
            shutil.rmtree(file)

    def _sort_data(self, dataset: type[DatasetChild]) -> None:
        if type(dataset) is AudioDataset:
            self._sort_audio_data(dataset)
            return
        if type(dataset) is SpectroDataset:
            self._sort_spectro_data(dataset)
            return

    def _sort_audio_data(self, data: AudioDataset) -> None:
        data_duration = data.data_duration
        sample_rate = data.sample_rate
        data_duration, sample_rate = (
            parameter if type(parameter) is not set else next(iter(parameter))
            for parameter in (data_duration, sample_rate)
        )
        data.move(
            self.folder
            / "data"
            / "audio"
            / f"{round(data_duration.total_seconds())}_{round(sample_rate)}",
        )

    def _sort_spectro_data(self, data: SpectroDataset) -> None:
        pass


DatasetChild = TypeVar("DatasetChild", bound=Dataset)
