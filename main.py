import sys

from dotenv import dotenv_values
from typing import Dict
import os
import time

from loguru import logger

from cloud import Cloud
from synchronization import Synchronization


class Main:
    @classmethod
    def __get_env(cls) -> Dict:
        """Метод для загрузки переменных окружения"""
        config: Dict = dotenv_values(".env")

        return config

    @classmethod
    def __logging_settings(cls, path_log_file: str):
        # Удаляем стандартный логгер
        logger.remove()
        # Добавляем свои
        logger.add(sink="logging.log",
                   format="synchronizer {time:YYYY-MM-DD HH:mm:ss,SSS} {level} {message}",
                   level="INFO",
                   rotation="1 MB",
                   compression="zip",)
        logger.add(sys.stdout, format="synchronizer {time:YYYY-MM-DD HH:mm:ss,SSS} {level} {message}")

    @classmethod
    def start(cls):
        """Метод для настройки приложения и запуска синхронизации файлов"""
        # Получаем переменные окружения
        config: Dict = cls.__get_env()

        # Путь до локальной папки с файлами
        path_sync_folder: str = config.get("PATH_SYNC_FOLDER")
        # Путь до папки в облаке
        path_cloud_folder: str = config.get("CLOUD_STORAGE_FOLDER")
        # Токен
        token: str = config.get('TOKEN')
        # Период синхронизации
        sync_period: int = int(config.get("SYNC_PERIOD"))
        # Путь к файлу с логами
        path_log_file: str = config.get("PATH_LOG_FILE")

        # Создаём логгер
        cls.__logging_settings(path_log_file=path_log_file)
        # Создаём экземпляр класса для работы с облаком
        cloud: Cloud = Cloud(token=token, dir_name=path_cloud_folder)
        # Создаём экземпляр класса для работы с синхронизацией
        synchronization: Synchronization = Synchronization(dir_path=path_sync_folder, cloud=cloud)

        # Проверяем существование указанной локальной директории
        if not os.path.exists(path_sync_folder):
            logger.critical(f"Указанной директории не существует {path_sync_folder}. Программа прекращает свою работу")
        # Проверяем исправность токена
        if not cloud.token_check():
            logger.critical(f"Указанный токен неисправен {token}. Программа прекращает свою работу")
        # запускаем программу
        else:
            # запускаем бесконечный цикл
            logger.info(f"Программа синхронизации файлов начинает работу с директорией {path_sync_folder}.")
            while True:
                # Синхронизируем файлы
                synchronization.synchronize()
                # Засыпаем на установленный период
                time.sleep(sync_period)


if __name__ == "__main__":
    Main.start()
