from typing import Dict, List
import os

from cloud import Cloud


class Synchronization:
    def __init__(self, dir_path: str, cloud: Cloud):
        self.__dir_path: str = dir_path
        self.__cloud: Cloud = cloud


    def __get_all_files(self) -> Dict[str, str]:
        files: Dict = dict()

        path_to_dir = os.path.abspath(self.__dir_path)

        for i_file in os.listdir(path_to_dir):
            file_path = os.path.abspath(os.path.join(path_to_dir, i_file))

            if os.path.isfile(file_path):
                file_name = os.path.basename(file_path)
                file_date = os.path.getmtime(file_path)

                files[file_name] = file_date

        return files

    def synchronize(self):
        result = self.__get_all_files()
        print(result)
