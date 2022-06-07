import os

import yaml

from api.utils.singleton import Singleton
from typing import List, Dict


class Config(metaclass=Singleton):
    def __init__(self, filename: str = None):
        if not filename:
            return
        reader = self.yaml_reader(filename=filename)
        self.ENDPOINT_HOST = reader.get('endpoint').get('host')
        self.ENDPOINT_PORT = reader.get('endpoint').get('port')

        self.LOG_LEVEL = reader.get('logger').get('level')

        self.DB_FACULTIES: List[Dict] = reader.get('database').get('faculties')
        self.DB_GROUPS: List[Dict] = reader.get('database').get('groups')
        self.DB_DAYS: List[str] = reader.get('database').get('days')
        self.DB_TIME_CELLS: List[Dict] = reader.get('database').get('time_cells')
        self.DB_DISCIPLINE_TYPES: List[str] = reader.get('database').get('discipline_types')

    @staticmethod
    def yaml_reader(filename):
        path = os.path.join(os.path.dirname(__file__), filename)
        with open(path) as file:
            return yaml.safe_load(file)
