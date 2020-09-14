
def groupby(items, key=lambda x: x):
    result = {}
    for i in items:
        k = key(i)
        category_items = result.get(k, [])
        category_items.append(i)
        if len(category_items) == 1:
            result[k] = category_items

    return result

def is_dead(item):
    return bool(item.get('isTombstone', False))

def find(func, iterable):
    try:
        return next(item for item in iterable if func(item))
    except StopIteration:
        return None

def for_each(func, iterable):
    for item in iterable:
        func(item)

def sub_category_is_hidden(sub_c_id):
    sub_c = sub_c_id.lookup()
    return sub_c.masterCategoryId == 'MasterCategory/__Hidden__'

def sub_category_sort_index(sub_c_id):
    sub_c = sub_c_id.lookup()
    master_c = sub_c.masterCategoryId.lookup()
    return "{}-{}".format(master_c.sortableIndex, sub_c.sortableIndex)
