from dotenv import dotenv_values
from typing import Dict
import time

from cloud import Cloud
from synchronization import Synchronization


class Main:
    @classmethod
    def __get_env(cls) -> Dict:
        """Метод для загрузки переменных окружения"""
        config = dotenv_values(".env")

        return config

    @classmethod
    def __logging_settings(cls, path_log_file: str):
        pass

    @classmethod
    def start(cls):
        """Метод для настройки приложения и запуска синхронизации файлов"""
        # Получаем переменные окружения
        config = cls.__get_env()

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

        # Создаём экземпляр класса для работы с облаком
        cloud = Cloud(token=token, dir_name=path_cloud_folder)
        # Создаём экземпляр класса для работы с синхронизацией
        synchronization = Synchronization(dir_path=path_sync_folder, cloud=cloud)

        # запускаем бесконечный цикл
        while True:
            # Синхронизируем файлы
            synchronization.synchronize()
            # Засыпаем на установленный период
            time.sleep(sync_period)


if __name__ == "__main__":
    Main.start()
