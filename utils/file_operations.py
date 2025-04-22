import json


def save_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def load_json(filename):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
