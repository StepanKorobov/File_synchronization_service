from typing import Dict, List
import datetime
import os

import requests


class Cloud:
    """
    Класс для работы с облаком
    """
    def __init__(self, token: str, dir_name: str):
        self.__headers: Dict[str, str] = {"Authorization": f"OAuth {token}"}
        self.__params: Dict[str, str] = {"path": dir_name}
        self.__dir_name: str = dir_name

    def files_info(self) -> Dict[str, float]:
        """
        Метод класса для получения информации о файлах в папке на облаке

        :return: список словарей с именем файла и временем последнего обновления
        :rtype: List[Dict]
        """
        # Новые параметры с учетом нужных полей
        params = self.__params.copy()
        params["fields"]: str = "_embedded.items.name, _embedded.items.modified"

        # Запрос на получение названия файлов и времени последнего обновления
        request = requests.get(
            url="https://cloud-api.yandex.net/v1/disk/resources",
            headers=self.__headers,
            params=params)
        # преобразуем в json
        result: Dict = request.json()
        # получаем список файлов
        files_list: List[Dict] = result["_embedded"]["items"]
        # словарь с файлами
        files_dict: Dict[str, float] = dict()

        for i_file in files_list:
            # Получаем время обновления файла строкой
            dt:str = i_file["modified"]
            # Получаем время обновления файла в корректном формате
            dt: datetime.datetime = datetime.datetime(
                year=int(dt[0:4]),
                month=int(dt[5:7]),
                day=int(dt[8:10]),
                hour=int(dt[11:13]),
                minute=int(dt[14:16]),
                second=int(dt[17:19]))
            # Сохраняем в словарь
            files_dict[i_file["name"]]:float = dt.timestamp()

        return files_dict


    def file_upload(self, file_path: str) -> None:
        pass

    def file_reload(self, file_path: str) -> None:
        pass

    def file_delete(self, file_name: str) -> None:
        pass
