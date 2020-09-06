import json
from jsobject import Object # type: ignore

def json_loads_js_style(data):

    def up(item):
        if isinstance(item, dict):
            return Object(item)
        return item

    return json.loads(data, object_hook=up)

def json_load_js_style(filename):
    return json_loads_js_style(filename.read())


def Object_recursive(item):
    def up(item):
        if isinstance(item, dict):
            return Object({k: Object_recursive(v) for k, v in item.items()})
        elif isinstance(item, list):
            return [Object_recursive(i) for i in item]
        else:
            return item

    return up(item)
