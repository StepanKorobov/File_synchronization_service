from typing import Dict
import os

from cloud import Cloud


class Synchronization:
    """
    Класс для синхронизации файлов
    """
    def __init__(self, dir_path: str, cloud: Cloud):
        self.__dir_path: str = dir_path
        self.__cloud: Cloud = cloud


    def __get_all_files(self) -> Dict[str, float]:
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
        """Метод для синхронизации файлов"""
        # Получаем словарь локальных файлов
        local_files: Dict[str, float] = self.__get_all_files()
        # Получаем словарь файлов из обака
        cloud_files: Dict[str, float] = self.__cloud.get_info()

        # Проверяем наличие файлов в облаке и дату последнего изменения
        for i_file, i_date in local_files.items():
            # Путь к локальному файлу
            file_path = os.path.abspath(os.path.join(self.__dir_path, i_file))
            # Если файла нет в облаке, то загружаем его
            if i_file not in cloud_files:
                self.__cloud.load(file_path=file_path)
            # Если файл обновился, то обновляем его в облаке
            elif i_date > cloud_files[i_file]:
                self.__cloud.load(file_path=file_path)

        # Проверяем отсутствие файлов в локальной папке
        delite_files = cloud_files.keys() - local_files.keys()
        # Удаляем все файлы, которых нет в локальной папке
        for i_file in delite_files:
            self.__cloud.delete(file_name=i_file)
