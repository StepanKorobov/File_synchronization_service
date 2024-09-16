import os
from datetime import datetime, timedelta
from time import gmtime, sleep, strftime
from typing import Dict, List

import requests
from loguru import logger
from requests.exceptions import ConnectionError


class Cloud:
    """
    Класс для работы с облаком
    """

    def __init__(self, token: str, dir_name: str):
        self.__headers: Dict[str, str] = {"Authorization": f"OAuth {token}"}
        self.__params: Dict[str, str] = {"path": dir_name, "limit": 999}
        self.__params_load: Dict[str, str] = {
            "path": dir_name,
            "overwrite": "false",
            "limit": 999,
        }
        self.__dir_name: str = dir_name

    @classmethod
    def __get_file_dict(cls, files_list: List[Dict[str, str]]) -> Dict[str, float]:
        """
        Метод для получения словаря из имён файлов и времени(timestamp)

        :param files_list: Список словарей состоящий из имени и времени файла
        :type files_list: List[Dict[str, str]]
        :return: Словарь с файлами и временем
        :rtype: Dict[str, float]
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
                second=int(dt[17:19]),
            )
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
                    params=self.__params,
                )

                # Если статус 200, значит токен исправен
                if request.status_code == 200:
                    return True

                return False

            except ConnectionError:
                # Если отсутствует подключение к интернету, ждём 10 секунд
                logger.error("Не удалось проверить токен. Ошибка соединения.")
                sleep(10)

    def get_info(self) -> Dict[str, float] | None:
        """
        Метод класса для получения информации о файлах в папке на облаке

        :return: список словарей с именем файла и временем последнего обновления
        :rtype: List[Dict]
        """
        # Новые параметры с учетом нужных полей
        params = self.__params.copy()
        # добавляем параметры, для получения только нужных полей(имя файла и дата изменения)
        params["fields"]: str = "_embedded.items.name, _embedded.items.modified"

        try:
            # Запрос на получение названия файлов и времени последнего обновления
            request = requests.get(
                url="https://cloud-api.yandex.net/v1/disk/resources",
                headers=self.__headers,
                params=params,
            )
            # Преобразуем в json
            result: Dict = request.json()
            # Получаем список файлов
            files_list: List[Dict[str, str]] = result["_embedded"]["items"]
            # Преобразуем список файлов в нужный нам формат
            files_dict: Dict[str, float] = self.__get_file_dict(files_list)

            return files_dict
        # в случае отсутствия соединения
        except ConnectionError:
            logger.error("Не удалось синхронизировать файлы. Ошибка соединения")
            return None

    def load(self, file_path: str) -> None:
        """
        Метод для загрузки файлов на облако

        :param file_path: путь к локальному файлу
        :type file_path: str
        :param rewrite: перезаписывать файл или нет, нужно при обновлении файла
        :type rewrite: bool
        """
        # Путь к локальному файлу
        path: str = os.path.abspath(file_path)
        # Имя файла
        file_name: str = os.path.basename(file_path)
        # Путь к файлу в облаке
        cloud_file_path: str = f"{self.__dir_name}/{file_name}"
        # параметры
        self.__params_load["path"] = cloud_file_path

        # Считываем локальный файл
        with open(path, "rb") as f:
            file = f.read()

        try:
            # Запрос на получение ссылки для загрузки файла в облако
            request = requests.get(
                url="https://cloud-api.yandex.net/v1/disk/resources/upload",
                headers=self.__headers,
                params=self.__params_load,
            )
            # Получаем url для загрузки файла
            url: str = request.json()["href"]

            # Загружаем файл в облако
            requests.put(url=url, data=file)

        except ConnectionError:
            if self.__params_load["overwrite"] == "false":
                logger.error(f"Файл {file_name} не записан. Ошибка соединения.")
            else:
                logger.error(f"Файл {file_name} не перезаписан. Ошибка соединения.")
        else:
            if self.__params_load["overwrite"] == "false":
                logger.info(f"Файл {file_name} успешно записан.")
            else:
                logger.info(f"Файл {file_name} успешно перезаписан.")

    def reload(self, file_path: str) -> None:
        """
        Метод для обновления файлов

        :param file_path: путь к локальному файлу
        :type file_path: str
        """
        self.__params_load["overwrite"] = "true"
        self.load(file_path=file_path)
        self.__params_load["overwrite"] = "false"

    def delete(self, file_name: str) -> None:
        """
        Метод для удаления файлов с облака

        :param file_name: путь к локальному файлу
        :type: str
        """
        # Путь к файлу в облаке
        cloud_file_path: str = f"{self.__dir_name}/{file_name}"

        try:
            requests.delete(
                url="https://cloud-api.yandex.net/v1/disk/resources",
                headers=self.__headers,
                params={"path": cloud_file_path},
            )
        except ConnectionError:
            logger.error(f"Файл {file_name} не удалён. Ошибка соединения.")
        else:
            logger.info(f"Файл {file_name} успешно удалён.")
