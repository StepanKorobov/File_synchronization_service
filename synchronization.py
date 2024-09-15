from typing import Dict, List
import os

from cloud import Cloud


class Synchronization:
    """
    Класс для синхронизации файлов
    """
    def __init__(self, dir_path: str, cloud: Cloud):
        self.__dir_path: str = dir_path
        self.__cloud: Cloud = cloud


    def __get_all_files(self) -> Dict[str, str]:
        """
        Метод для получения всех файлов из папки на локальном диске

        :return: словарь с именами файлов и датой обновления
        :rtype: Dict[str, str]
        """
        # Словарь с названием файлов и датой последнего обновления
        files: Dict = dict()

        # Путь к папке с файлами
        path_to_dir: str = os.path.abspath(self.__dir_path)

        # В цикле проходимся по папке, нам нужны только файлы
        for i_file in os.listdir(path_to_dir):
            # Путь до файла/папки
            file_path: str = os.path.abspath(os.path.join(path_to_dir, i_file))

            # Если файл, то сохраняем путь и время в словаре
            if os.path.isfile(file_path):
                file_name: str = os.path.basename(file_path)
                file_date: float = os.path.getmtime(file_path)

                files[file_name]: float = file_date

        # возвращаем словарь с файлами
        return files

    def synchronize(self):
        result = self.__get_all_files()
        print(result)
