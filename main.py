import os
import time
from dotenv import dotenv_values

from cloud import Cloud
from synchronization import Synchronization


class Main:
    @classmethod
    def __get_env(cls):
        """Метод для загрузки переменных окружения"""
        config = dotenv_values(".env")
        print(type(config))

        return config

    @classmethod
    def __logging_settings(cls, path_log_file: str):
        pass

    @classmethod
    def start(cls):
        config = cls.__get_env()

        path_sync_folder: str = config.get("PATH_SYNC_FOLDER")
        path_cloud_folder: str = config.get("CLOUD_STORAGE_FOLDER")
        token: str = config.get('TOKEN')
        sync_period: int = int(config.get("SYNC_PERIOD"))
        path_log_file: str = config.get("PATH_LOG_FILE")

        cloud = Cloud(token=token, dir_name=path_cloud_folder)
        synchronization = Synchronization(dir_path=path_sync_folder, cloud=cloud)

        while True:
            synchronization.synchronize()
            time.sleep(sync_period)


if __name__ == "__main__":
    Main.start()
