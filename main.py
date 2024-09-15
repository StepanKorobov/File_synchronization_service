import os
from dotenv import dotenv_values

from cloud import Cloud
from synchronization import Synchronization

class Main:
    @classmethod
    def __get_env(cls):
        """Метод для загрузки переменных окружения"""
        config = dotenv_values(".env")

        return config

    @classmethod
    def start(cls):
        config = cls.__get_env()



if __name__ == "__main__":
    # main()
    Main.get_env()

