from datetime import datetime, timedelta
from time import strftime, gmtime, sleep
from typing import Dict, List
import os

from loguru import logger
from requests.exceptions import ConnectionError
import requests


class Cloud:
    """
    Класс для работы с облаком
    """

    def __init__(self, token: str, dir_name: str):
        self.__headers: Dict[str, str] = {"Authorization": f"OAuth {token}"}
        self.__params: Dict[str, str] = {"path": dir_name}
        self.__dir_name: str = dir_name


    @classmethod
    def __get_file_dict(cls, files_list: List[Dict[str, str]]) -> Dict[str, float]:
        """
        Метод для получения словаря из имён файлов и времени(timestamp)

        :param files_list: Список словарей состоящий из имени и времени файла
        :return:
        """

        # Создаем словарь для файлов
        files_dict: Dict[str, float] = dict()
        # Локальная временная зона (у яндекс диска +0), нужно для корректной синхронизации файлов
        time_utc = strftime("%z", gmtime())
        time_utc = int(time_utc[1:3])

        # В цикле проходимся по всем файлам для добавления в словарь
        for i_file in files_list:
            # Получаем время обновления файла строкой
            dt: str = i_file["modified"]
            # Получаем время обновления файла в корректном формате
            date_time: datetime = datetime(
                year=int(dt[0:4]),
                month=int(dt[5:7]),
                day=int(dt[8:10]),
                hour=int(dt[11:13]),
                minute=int(dt[14:16]),
                second=int(dt[17:19]), )
            correct_dt = date_time + timedelta(hours=time_utc)
            # Сохраняем в словарь
            files_dict[i_file["name"]]: float = correct_dt.timestamp()

        return files_dict

    def token_check(self) -> bool:
        """
        Метод для проверки токена

        :return: Возвращает True, если токен рабочий, иначе False
        :rtype: bool
        """

        while True:
            try:
                # Делаем запрос на получение информации
                request = requests.get(
                    url="https://cloud-api.yandex.net/v1/disk/resources",
                    headers=self.__headers,
                    params=self.__params)

                # Если статус 200, значит токен исправен
                if request.status_code == 200:
                    return True

                return False

            except ConnectionError:
                # Если отсутствует подключение к интернету, ждём 10 секунд
                logger.error("Не удалось проверить токен - отсутствует подключение к интернету")
                sleep(10)



    def get_info(self) -> Dict[str, float]:
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
        # Преобразуем в json
        result: Dict = request.json()
        # Получаем список файлов
        files_list: List[Dict[str, str]] = result["_embedded"]["items"]

        files_dict: Dict[str, float] = self.__get_file_dict(files_list)

        return files_dict

    def load(self, file_path: str) -> None:
        """
        Метод для загрузки файлов на облако

        :param file_path: путь к локальному файлу
        :type file_path: str
        """
        # Путь к локальному файлу
        path = os.path.abspath(file_path)
        # Имя файла
        file_name = os.path.basename(file_path)
        # Путь к файлу в облаке
        cloud_file_path = f"{self.__dir_name}/{file_name}"

        # Считываем локальный файл
        with open(path, "rb") as f:
            file = f.read()

        # Запрос на получение ссылки для загрузки файла в облако
        request = requests.get(
            url="https://cloud-api.yandex.net/v1/disk/resources/upload",
            headers=self.__headers,
            params={"path": cloud_file_path, "overwrite": "true"})
        # Получаем url для загрузки файла
        url = request.json()["href"]
        # Загружаем файл в облако
        request_put = requests.put(url=url, data=file)

    def reload(self, file_path: str) -> None:
        """Метод для обновления файлов"""
        self.load(file_path)

    def delete(self, file_name: str) -> None:
        """
        Метод для удаления файлов с облака

        :param file_name: путь к локальному файлу
        :type: str
        """
        # Путь к файлу в облаке
        cloud_file_path: str = f"{self.__dir_name}/{file_name}"

        request = requests.delete(
            url="https://cloud-api.yandex.net/v1/disk/resources",
            headers=self.__headers,
            params={"path": cloud_file_path})
