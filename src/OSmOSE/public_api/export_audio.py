import argparse
import os
from pathlib import Path

from OSmOSE.core_api.audio_dataset import AudioDataset

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    required = parser.add_argument_group("required arguments")
    required.add_argument(
        "--dataset-json-path",
        "-p",
        required=True,
        help="The path to the AudioDataset JSON file.",
        type=str,
    )
    required.add_argument(
        "--output-folder",
        "-o",
        required=True,
        help="The path to the folder in which the reshaped files are written.",
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
        "--subtype",
        "-s",
        required=False,
        help="The subtype format of the audio files to export.",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--umask",
        type=int,
        default=0o002,
        help="The umask to apply on the created file permissions.",
    )

    args = parser.parse_args()
    subtype = None if args.subtype.lower() == "none" else args.subtype

    os.umask(args.umask)

    ads = AudioDataset.from_json(Path(args.dataset_json_path))
    ads.write(
        folder=Path(args.output_folder),
        subtype=subtype,
        first=args.first,
        last=args.last,
    )
