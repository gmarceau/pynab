from forbiddenfruit import curse
from json_objects import json_load_js_style
from utils import is_dead, for_each

def create_index(data):
    result = {}

    def recur(item):
        if isinstance(item, dict):
            if 'entityId' in item:
                result[item.entityId] = item
            for v in item.values():
                recur(v)
        elif isinstance(item, list):
            for v in item:
                recur(v)

    recur(data)
    return result


top_budget = None
def lookup_entity_id(self):
    return top_budget.index[self]
curse(str, "lookup", lookup_entity_id)


def filter_tombstones(item):
    if isinstance(item, dict):
        for_each(filter_tombstones, item.values())
    elif isinstance(item, list):
        item[:] = [sub for sub in item if not is_dead(sub)]
        for_each(filter_tombstones, item)

def load_budget(path):
    global top_budget

    if path.is_dir():
        path = find_full_budget(path)

    if not path or not path.exists():
        raise(Exception("Unable to guess budget location"))

    data =  json_load_js_style(path)
    filter_tombstones(data)
    data['index'] = create_index(data)
    top_budget = data

    data.transactions == sorted(data.transactions, key=lambda t: t.date)

    return(data)
