from collections import namedtuple
from distutils.errors import UnknownFileError
import shutil
import os
from typing import Union, NamedTuple
import json
import tomllib

def display_folder_storage_infos(dir_path: str) -> None:

    usage=shutil.disk_usage(dir_path)
    print("Total storage space (TB):",round(usage.total / (1024**4),1))
    print("Used storage space (TB):",round(usage.used / (1024**4),1))
    print('-----------------------')
    print("Available storage space (TB):",round(usage.free / (1024**4),1))
    
def list_not_built_datasets(datasets_folder_path: str) -> None:
    """Prints the available datasets that have not been built by the `Dataset.build()` function.
    
        Parameter:
        ----------
        dataset_folder_path: The path to the directory containing the datasets"""

    dataset_list = [directory for directory in sorted(os.listdir(datasets_folder_path)) if os.path.isdir(directory) ]

    list_not_built_datasets = []

    for dataset_directory in dataset_list:

        if os.path.exists(os.path.join(datasets_folder_path,dataset_directory,'raw/audio/original/') ):
            list_not_built_datasets.append(dataset_directory)

    print("List of the datasets not built yet:")

    for dataset in list_not_built_datasets:
        print("  - {}".format(dataset))    
    
def read_config(raw_config: Union[str, dict]) -> NamedTuple:
        """Read the given configuration file or dict and converts it to a namedtuple. Only TOML and JSON formats are accepted for now.
        
            Parameter:
                raw_config: the path of the configuration file, or the dict object containing the configuration.
                
            Returns:
                The configuration as a NamedTuple object."""
                
        if isinstance(raw_config, str):
            if not os.path.isfile(raw_config):
                raise FileNotFoundError(f"The configuration file {raw_config} does not exist.")
            
            with open(raw_config, "rb") as input_config:
                match os.path.splitext(raw_config)[1]:
                    case "toml":
                        pre_config = tomllib.load(input_config)
                    case "json":
                        pre_config = json.load(input_config)
                    case "yaml":
                        raise NotImplementedError("YAML support will eventually get there (unfortunately)")
                    case _:
                        raise UnknownFileError(f"The provided configuration file extension (.{os.path.splitext(raw_config)[1]} is not a valid extension. Please use .toml or .json files.")

        return namedtuple('GenericDict', pre_config.keys())(**pre_config)