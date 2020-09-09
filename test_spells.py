#!/usr/bin/env python
import pytest
from pprint import pprint
from spells import shells, Spell, beam_to
from json_objects import Object_recursive, Object
from utils import groupby
from transactions import transaction_month

class MonthlyTransactionsSpell(Spell):

    def _detect(v):
        if type(v) != dict:
            return False
        if not v:
            return True
        lst = next(iter(v.values()))
        if type(lst) != list:
            return False
        if not lst:
            return True
        item = lst[0]
        if type(item) not in {dict, Object}:
            return False

        return item.get('entityType') == 'transaction'

MonthlyTransactionsSpell.study_globally()
def test_monthly_transaction_spell_detect():
    input = {'2014-03': [{'date': '2014-03-04', 'entityId':
                          'B850E42E-B8B0-AE20-C396-417D83E94D9C', 'entityType': 'transaction',
                          'accepted': True, 'amount': 200, 'entityVersion': 'A-73', 'cleared':
                          'Cleared', 'payeeId': '30ACAD6C-2080-18C4-4D9B-417D050FC81C', 'categoryId':
                          None, 'accountId': 'A4E12926-829B-E223-CA1F-417D83E2CD01'},
                         {'date':
                          '2014-03-04', 'entityId': '9D8AE375-06CA-E554-21FB-417D96CE437C',
                          'entityType': 'transaction', 'accepted': True, 'amount': -100,
                          'entityVersion': 'A-75', 'cleared': 'Uncleared', 'payeeId':
                          '923CF0E7-F3BF-52C3-2D05-417DDAF133C5', 'categoryId': 'A18', 'accountId':
                          '553C9C0B-0646-3894-7C27-417D5B7E264B'}]}
    assert(MonthlyTransactionsSpell._detect(input))

class TransactionsSpell(Spell):
    @staticmethod
    def _detect(v):
        return type(v) == list and \
            ((not v) or (v[0].get('entityType') == 'transaction'))

    def balance(self):
        return sum(t.amount for t in self)

    @beam_to(MonthlyTransactionsSpell)
    def beam_to_montly(self):
        return groupby(self, key=transaction_month)
        assert(MonthlyTransactionsSpell._detect(result))
        return result

TransactionsSpell.study_globally()



transactions = Object_recursive([{"date": "2014-03-04",
                                  "entityId": "B850E42E-B8B0-AE20-C396-417D83E94D9C",
                                  "entityType": "transaction",
                                  "accepted": True,
                                  "amount": 200,
                                  "entityVersion": "A-73",
                                  "cleared": "Cleared",
                                  "payeeId": "30ACAD6C-2080-18C4-4D9B-417D050FC81C",
                                  "categoryId": None,
                                  "accountId": "A4E12926-829B-E223-CA1F-417D83E2CD01"},
                                 {"date": "2014-03-04",
                                  "entityId": "9D8AE375-06CA-E554-21FB-417D96CE437C",
                                  "entityType": "transaction",
                                  "accepted": True,
                                  "amount": -100,
                                  "entityVersion": "A-75",
                                  "cleared": "Uncleared",
                                  "payeeId": "923CF0E7-F3BF-52C3-2D05-417DDAF133C5",
                                  "categoryId": "A18",
                                  "accountId": "553C9C0B-0646-3894-7C27-417D5B7E264B"
                                 }])

def test_spell_on_transactions_list():
    global shells
    a = transactions.up()
    print('--33', dict(shells))

    assert(id(transactions) != id(a))
    assert(len(a) == 2)
    assert(set(a[0].keys()) == {'date', 'entityType', 'entityId', 'accepted', 'amount', 'entityVersion', 'cleared', 'payeeId', 'categoryId', 'accountId'})
    pprint(a)
    assert(a.balance() == 100)
    assert(a.balance() == 100)
    b = transactions.up()
    assert(id(transactions) != id(a))
    assert(id(b) == id(a))
    assert(len(b) == 2)
    assert(set(b[0].keys()) == {'date', 'entityType', 'entityId', 'accepted', 'amount', 'entityVersion', 'cleared', 'payeeId', 'categoryId', 'accountId'})
    pprint(b)
    assert(b.balance() == 100)
    assert(b.balance() == 100)
    assert(len(shells) == 1)
    assert(id(a.down()) == id(transactions))
    assert(len(shells) == 0)

def test_spell_weakref():
    a = transactions.up()
    assert(len(shells) == 1)
    del a
    assert(len(shells) == 0)



def test_beams_to():
    actual = transactions.up().to(MonthlyTransactionsSpell)
    expected = {'2014-03': [{'date': '2014-03-04', 'entityId':
                             'B850E42E-B8B0-AE20-C396-417D83E94D9C', 'entityType': 'transaction',
                             'accepted': True, 'amount': 200, 'entityVersion': 'A-73', 'cleared':
                             'Cleared', 'payeeId': '30ACAD6C-2080-18C4-4D9B-417D050FC81C', 'categoryId':
                             None, 'accountId': 'A4E12926-829B-E223-CA1F-417D83E2CD01'},
                            {'date':
                             '2014-03-04', 'entityId': '9D8AE375-06CA-E554-21FB-417D96CE437C',
                             'entityType': 'transaction', 'accepted': True, 'amount': -100,
                             'entityVersion': 'A-75', 'cleared': 'Uncleared', 'payeeId':
                             '923CF0E7-F3BF-52C3-2D05-417DDAF133C5', 'categoryId': 'A18', 'accountId':
                             '553C9C0B-0646-3894-7C27-417D5B7E264B'}]}

    assert(actual.down() == expected)

if __name__ == '__main__':
    import sys
    pytest.main(args=sys.argv)
