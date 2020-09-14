#!/usr/bin/env python
import pytest
from plumbum import local
from transactions import play_transaction, play_monthly_transactions_category
from json_objects import Object_recursive
from load_budget import load_budget

class TestTransactions:
    @pytest.fixture(autouse=True)
    def load_budget(self):
        self.budget = load_budget(local.path('example-budget.yfull.json'))
        yield

    def test_play_one_transaction(self):
        assert play_transaction(self.budget.transactions[0]) == 1000

    def test_play_one_split_transaction(self):
        t = Object_recursive({
	    "subTransactions": [
		{
		    "categoryId": "A52",
		    "entityVersion": "A-1384",
		    "amount": 992.32,
		    "parentTransactionId": "Transaction/YNAB:1,814.71:2012-07-09:1",
		    "entityId": "F76BDD01-28CA-3DD2-A3BA-CEC3645E8D6E",
		    "entityType": "subTransaction"
		},
		{
		    "targetAccountId": "A6",
		    "transferTransactionId": "9A0F222B-0961-65D0-F7D9-CEC3650AB0F9_T_0",
		    "categoryId": None,
		    "entityVersion": "A-571",
		    "amount": 822.39,
		    "parentTransactionId": "Transaction/YNAB:1,814.71:2012-07-09:1",
		    "entityId": "9A0F222B-0961-65D0-F7D9-CEC3650AB0F9",
		    "entityType": "subTransaction"
		}
	    ],
	    "categoryId": "Category/__Split__",
	    "amount": 1814.71,
	    "accountId": "A4",
	})
        assert play_transaction(t) == 992.32
        assert play_transaction(t, categoryId='A52') == 992.32
        assert play_transaction(t, categoryId='Treats') == 0
        assert play_transaction(t, accountId='A4') == 1814.71
        assert play_transaction(t, accountId='Something else') == 0

    def test_play_transaction_1(self):
        actual = play_transaction(self.budget.transactions[0], categoryId='Category/__ImmediateIncome__')
        assert actual == 1000

    def test_play_transactions(self):
        actual = play_transaction(self.budget.transactions[1], categoryId='Category/__ImmediateIncome__')
        assert actual == 500

    def test_play_monthly_transaction(self):
        actual = play_monthly_transactions_category(self.budget, '2014-02', 'Category/__ImmediateIncome__')
        assert actual == 1500
        actual = play_monthly_transactions_category(self.budget, '2014-02', 'A18')
        assert actual == -100

if __name__ == '__main__':
    import sys
    pytest.main(args=sys.argv)
