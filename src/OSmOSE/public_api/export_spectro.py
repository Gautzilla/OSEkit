import argparse
import os
from pathlib import Path

from OSmOSE.core_api.spectro_dataset import SpectroDataset
from OSmOSE.public_api import Analysis


def write_spectro_files(
    sds: SpectroDataset,
    analysis: Analysis,
    matrix_folder: Path,
    spectrogram_folder: Path,
    link: bool = True,
    first: int = 0,
    last: int | None = None,
) -> None:
    """Write SpectroDataset output files to disk.

    Parameters
    ----------
    sds: SpectroDataset
        The SpectroDataset of which the data should be written.
    analysis: Analysis
        Flags that should be use to specify the type of analysis to run.
        See Dataset.Analysis docstring for more info.
    matrix_folder: Path
        The folder in which the matrix npz files should be written.
    spectrogram_folder: Path
        The folder in which the spectrogram png files should be written.
    link: bool
        If set to True, the ads data will be linked to the exported files.
    first: int
        Index of the first data object to write.
    last: int|None
        Index after the last data object to write.

    Returns
    -------

    """
    if Analysis.MATRIX in analysis and Analysis.SPECTROGRAM in analysis:
        sds.save_all(
            matrix_folder=matrix_folder,
            spectrogram_folder=spectrogram_folder,
            link=link,
            first=first,
            last=last,
        )
    elif Analysis.SPECTROGRAM in analysis:
        sds.save_spectrogram(
            folder=spectrogram_folder,
            first=first,
            last=last,
        )
    elif Analysis.MATRIX in analysis:
        sds.write(
            folder=matrix_folder,
            link=link,
            first=first,
            last=last,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    required = parser.add_argument_group("required arguments")
    required.add_argument(
        "--dataset-json-path",
        "-p",
        required=True,
        help="The path to the SpectroDataset JSON file.",
        type=str,
    )
    required.add_argument(
        "--analysis",
        "-a",
        required=True,
        help="Flags representing which files to export during this analysis.",
        type=int,
    )
    required.add_argument(
        "--matrix-folder",
        "-m",
        required=True,
        help="The path to the folder in which the npz matrix files are written.",
        type=str,
    )
    required.add_argument(
        "--spectrogram-folder",
        "-s",
        required=True,
        help="The path to the folder in which the png spectrogram files are written.",
        type=str,
    )
    required.add_argument(
        "--first",
        "-f",
        required=True,
        help="The index of the first file to export.",
        type=int,
        default=0,
    )
    required.add_argument(
        "--last",
        "-l",
        required=True,
        help="The index after the last file to export.",
        type=int,
        default=-1,
    )
    parser.add_argument(
        "--umask",
        type=int,
        default=0o002,
        help="The umask to apply on the created file permissions.",
    )

    args = parser.parse_args()

    os.umask(args.umask)

    sds = SpectroDataset.from_json(Path(args.dataset_json_path))

    analysis = Analysis(args.analysis)

    write_spectro_files(
        sds=sds,
        analysis=analysis,
        matrix_folder=Path(args.matrix_folder),
        spectrogram_folder=Path(args.spectrogram_folder),
        first=args.first,
        last=args.last,
        link=True,
    )

    sds.write_json(sds.folder)
