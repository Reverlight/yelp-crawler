import json


def dump_json(name, data):
    with open(name, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=6)
