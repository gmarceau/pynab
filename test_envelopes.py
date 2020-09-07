#!/usr/bin/env python
import pytest
from pprint import pprint
from plumbum import local
from json_objects import Object_recursive
from envelopes import walk_budget, play_transactions, play_monthly_transactions
from ynabparse import load_budget

class TestEnvelopes:
    @pytest.fixture(autouse=True)
    def load_budget(self):
        self.budget = load_budget(local.path('example-budget.yfull.json'))
        yield

    def test_play_transactions(self):
        actual = play_transactions(self.budget.transactions, 'Category/__ImmediateIncome__')
        assert(actual == 3000)

    def test_play_monthly_transaction(self):
        actual = play_monthly_transactions(self.budget, '2014-02', 'Category/__ImmediateIncome__')
        assert(actual == 1500)
        actual = play_monthly_transactions(self.budget, '2014-02', 'A18')
        assert(actual == -100)

    def test_walk_budget_with_one_month(self):
            budget = Object_recursive({
                "monthlyBudgets": [
                    {
                            "month": "2012-06-01",
                            "monthlySubCategoryBudgets": [
                                    {
                                            "categoryId": "A28",
                                            "budgeted": 460,
                                            "overspendingHandling": None,
                                            "entityVersion": "A-0",
                                            "parentMonthlyBudgetId": "MB/2012-06",
                                            "entityId": "MCB/2012-06/A28",
                                            "entityType": "monthlyCategoryBudget"
                                    },
                                    {
                                            "categoryId": "A29",
                                            "budgeted": 80,
                                            "overspendingHandling": None,
                                            "entityVersion": "A-0",
                                            "parentMonthlyBudgetId": "MB/2012-06",
                                            "entityId": "MCB/2012-06/A29",
                                            "entityType": "monthlyCategoryBudget"
                                    },

                            ],
                            "entityVersion": "A-0",
                            "entityId": "MB/2012-06",
                            "entityType": "monthlyBudget"
                    }
                ],
                "transactions": [
                    {
                            "date": "2012-06-13",
                            "source": "ImportedIphone",
                            "entityId": "A128",
                            "entityType": "transaction",
                            "categoryId": "A28",
                            "entityVersion": "A-3458",
                            "amount": -4,
                            "accountId": "A6",
                            "cleared": "Reconciled",
                            "accepted": True
                    },
                    {
                            "date": "2012-06-13",
                            "source": "ImportedIphone",
                            "entityId": "A129",
                            "entityType": "transaction",
                            "categoryId": "A29",
                            "entityVersion": "A-3457",
                            "amount": -60,
                            "accountId": "A6",
                            "cleared": "Reconciled",
                            "accepted": True
                    },
                    {
                            "date": "2012-06-14",
                            "source": "ImportedIphone",
                            "entityId": "A130",
                            "entityType": "transaction",
                            "categoryId": "A29",
                            "entityVersion": "A-3456",
                            "amount": -60.53,
                            "accountId": "A6",
                            "cleared": "Reconciled",
                            "accepted": True
                    },
                    {
                            "date": "2012-06-16",
                            "source": "ImportedIphone",
                            "entityId": "A131",
                            "entityType": "transaction",
                            "categoryId": "A28",
                            "entityVersion": "A-3455",
                            "amount": -9.18,
                            "accountId": "A6",
                            "cleared": "Reconciled",
                            "accepted": True
                    }],

            })
            actual = walk_budget(budget, 'A28')
            expected = [
                {"month": "2012-06",
                 "balance": 446.82,
                 "outflows": -13.18,
                 "budgeted": 460,
                 "overspendingHandling": "AffectsBuffer",
                 'entityType': 'monthlyEnvelopResult',
                 'monthlySubCategoryBudgetsId': 'MB/2012-06'
                }
            ]
            assert(actual == expected)

            actual = walk_budget(budget, 'A29')
            expected = [
                {"month": "2012-06",
                 "balance": -40.53,
                 "outflows": -120.53,
                 "budgeted": 80,
                 "overspendingHandling": "AffectsBuffer",
                 'entityType': 'monthlyEnvelopResult',
                 'monthlySubCategoryBudgetsId': 'MB/2012-06'
                }
            ]
            assert(actual == expected)
if __name__ == '__main__':
    import sys
    pytest.main(args=sys.argv)
