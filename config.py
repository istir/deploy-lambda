import json
from typing import Any

from my_types import ConfigSchema


class Config:

    def __init__(self):
        self.config = self.load_config()

    def load_config(self) -> ConfigSchema:
        data = ""
        with open("./config.json", "r") as f:
            data = f.read()
        return json.loads(data)

    def parse_config(self, conf: dict[str, Any]) -> ConfigSchema:
        response: ConfigSchema = {}  # type: ignore
        for key in conf:
            response[key] = conf[key]

        for key in ConfigSchema.__annotations__.keys():
            if key not in conf:
                response[key] = ""
        return response

    def get_config(self):
        return self.config


config = Config()
