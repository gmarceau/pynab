#!/usr/bin/env python
import pytest
from plumbum import local
from json_objects import json_loads_js_style, Object_recursive
from ynabparse import load_budget
from pprint import pprint

class TestYnabParse:

    @pytest.fixture(autouse=True)
    def load_budget(self):
        self.budget = load_budget(local.path('example-budget.yfull.json'))
        yield

    def test_json_loads(self):
        actual = json_loads_js_style('{"a": [{"b":1}, {"b":2}]}')
        assert(actual == {'a': [{'b': 1}, {'b': 2}]})
        assert(actual.a == [{'b': 1}, {'b': 2}])
        assert(actual.a[1].b == 2)

    def test_has_top_keys(self):
        expected = {'payees', 'budgetMetaData', 'accounts', 'accountMappings', 'fileMetaData', 'transactions', 'scheduledTransactions', 'masterCategories', 'monthlyBudgets', 'index'}
        assert(set(self.budget.keys()) == expected)

    def test_payees(self):
        expected = {'Target', 'Transfer : Off-Budget', 'Transfer : Checking', 'Starting Balance', 'Transfer : Savings'}
        actual = {p.name for p in self.budget.payees}
        assert(actual == expected)


if __name__ == '__main__':
    import sys
    pytest.main(args=sys.argv)
