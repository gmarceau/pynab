def is_dead(item):
    return bool(item.get('isTombstone', False))

def transaction_month(t):
    return t.date[0:7]

def transactions_by_month(transactions):
    from collections import OrderedDict
    from itertools import groupby

    return OrderedDict({k: list(v) for k, v in
                        groupby(sorted(transactions, key=lambda t: t.date),
                                key=transaction_month)})
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
