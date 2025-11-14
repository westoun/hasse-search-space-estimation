from datetime import datetime
import json


def save_to_json(obj, path: str) -> None:
    with open(path, "w") as config_file:
        json.dump(obj, config_file)


def get_timestamp() -> str:
    return str(datetime.now())
