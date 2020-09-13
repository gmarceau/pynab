#!/usr/bin/env python
import pytest
from pprint import pprint
from plumbum import local
from load_budget import load_budget
from ad_hoc import liquid_position

class TestAdHoc:

    def test_liquid_positions(self):
        input = load_budget(local.path('example-budget.yfull.json'))
        actual = liquid_position(input)
        actual = list(actual.items())[0:3]
        expected = [('2014-02',
                     {'Checking': 400, 'Off-Budget': 200, 'Savings': 1000, 'total': 1600}),
                    ('2014-03',
                     {'Checking': 800, 'Off-Budget': 400, 'Savings': 2000, 'total': 3200}),
                    ('2014-04',
                     {'Checking': 800, 'Off-Budget': 400, 'Savings': 2000, 'total': 3200})]
        assert(actual == expected)

if __name__ == '__main__':
    import sys
    pytest.main(args=sys.argv)
