def is_dead(item):
    return bool(item.get('isTombstone', False))

def transaction_month(t):
    return t.date[0:7]

def find(func, iterable):
    try:
        return next(item for item in iterable if func(item))
    except StopIteration:
        return None

def for_each(func, iterable):
    for item in iterable:
        func(item)

def sub_category_is_dead(sub_c_id):
    sub_c = sub_c_id.lookup()
    return sub_c.masterCategoryId == 'MasterCategory/__Hidden__' or is_dead(sub_c)

def sub_category_sort_index(sub_c_id):
    sub_c = sub_c_id.lookup()
    master_c = sub_c.masterCategoryId.lookup()
    return "{}-{}".format(master_c.sortableIndex, sub_c.sortableIndex)
