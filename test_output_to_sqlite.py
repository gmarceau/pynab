#!/usr/bin/env python
import pytest
import dataset
from plumbum import local
import output_to_sqlite
from output_to_sqlite import OutputToSqlite
from jsobject import Object
from json_objects import Object_recursive

class TestOutputToSqlite:

    @property
    def db_file(self):
        return local.path('test.sqlite')

    @property
    def db(self):
        return dataset.connect('sqlite:///{}'.format(self.db_file))

    def test_payees(self):
        input = Object_recursive({'payees': [
	    {
		"enabled": True,
		"entityVersion": "A-65",
		"entityId": "Payee/Transfer:F63FCDAB-2D87-51A5-08DB-417D04F32BDF",
		"entityType": "payee",
		"renameConditions": None,
		"autoFillMemo": None,
		"autoFillAmount": 0,
		"targetAccountId": "F63FCDAB-2D87-51A5-08DB-417D04F32BDF",
		"locations": None,
		"autoFillCategoryId": None,
		"name": "Transfer : Savings"
	    },
	    {
		"enabled": False,
		"entityVersion": "A-67",
		"entityId": "30ACAD6C-2080-18C4-4D9B-417D050FC81C",
		"entityType": "payee",
		"renameConditions": None,
		"autoFillMemo": None,
		"autoFillAmount": 0,
		"locations": None,
		"autoFillCategoryId": None,
		"name": "Starting Balance"
	    }]})
        o = OutputToSqlite(input, self.db_file)
        o.do_json_array('payees')
        assert(len(self.db['payees']) == 2)

    def test_transactions(self):
        input = Object_recursive({"transactions": [
		{
			"importedPayee": "DDA Deposit",
			"date": "2012-10-05",
			"subTransactions": [
				{
					"categoryId": "A19",
					"entityVersion": "A-1323",
					"amount": 350,
					"memo": "wedding gift",
					"parentTransactionId": "Transaction/YNAB:3,018.22:2012-10-05:1",
					"entityId": "95C57881-CBA4-9ACB-C9FD-56BA207B82FB",
					"entityType": "subTransaction"
				},
				{
					"categoryId": "A52",
					"entityVersion": "A-1325",
					"amount": 2668.22,
					"parentTransactionId": "Transaction/YNAB:3,018.22:2012-10-05:1",
					"entityId": "97265550-4119-9130-12DD-56BA20C98328",
					"entityType": "subTransaction"
				}
			],
			"YNABID": "YNAB:3,018.22:2012-10-05:1",
			"FITID": "2012279220007000320000000000000000000000004100000301822",
			"source": "Imported",
			"entityId": "Transaction/YNAB:3,018.22:2012-10-05:1",
			"entityType": "transaction",
			"categoryId": "Category/__Split__",
			"payeeId": "CA05F58C-2503-FE10-CFE4-CE724910F098",
			"entityVersion": "A-2238",
			"amount": 3018.22,
			"accountId": "A4",
			"cleared": "Reconciled",
			"accepted": True
		},
		{
			"importedPayee": "FOODTOWN #598",
			"date": "2012-10-05",
			"YNABID": "YNAB:-166.44:2012-10-05:1",
			"FITID": "2012279512000000559900000000000512000551822800000016644",
			"source": "Imported",
			"entityId": "Transaction/YNAB:-166.44:2012-10-05:1",
			"entityType": "transaction",
			"categoryId": "A17",
			"payeeId": "3BC5B4C1-F4C7-CA03-F94B-566F89920576",
			"entityVersion": "A-2236",
			"amount": -166.44,
			"accountId": "A4",
			"memo": "POS DEB 1226 10/05/12 00607365",
			"cleared": "Reconciled",
			"accepted": True
		},
		{
			"importedPayee": "PEPE VERDE TOGO",
			"date": "2012-10-05",
			"YNABID": "YNAB:-16.22:2012-10-05:1",
			"FITID": "2012279312000000086600000000000512000551922900000001622",
			"source": "Imported",
			"entityId": "Transaction/YNAB:-16.22:2012-10-05:1",
			"entityType": "transaction",
			"categoryId": "A30",
			"payeeId": "2DEAE4BF-CF4B-326D-622A-566F8B6741AE",
			"entityVersion": "A-2237",
			"amount": -16.22,
			"accountId": "A4",
			"memo": "DBT CRD 1911 10/04/12 00019797",
			"cleared": "Reconciled",
			"accepted": True
		}]})

        o = OutputToSqlite(input, self.db_file)
        o.do_transactions()
        assert(len(self.db['transactions']) == 3)
        assert(len(self.db['subTransactions']) == 2)

    def test_master_categories(self):
        input = Object_recursive({"masterCategories":
                                  [{
                                      "type": "OUTFLOW",
                                      "deleteable": True,
                                      "name": "Generosity",
                                      "subCategories": [
                                          {
	                                      "type": "OUTFLOW",
	                                      "name": "Charity & Protests",
	                                      "cachedBalance": 0,
	                                      "masterCategoryId": "A13",
	                                      "entityVersion": "A-6205",
	                                      "entityId": "A14",
	                                      "sortableIndex": 0,
	                                      "entityType": "category"
                                          },
                                          {
	                                      "type": "OUTFLOW",
	                                      "name": "Spontanous Gifts",
	                                      "cachedBalance": 0,
	                                      "masterCategoryId": "A13",
	                                      "entityVersion": "A-8",
	                                      "entityId": "A15",
	                                      "sortableIndex": 1073741823,
	                                      "entityType": "category"
                                          },
                                          {
	                                      "type": "OUTFLOW",
	                                      "name": "Christmas & Birthday Gifts",
	                                      "cachedBalance": 0,
	                                      "masterCategoryId": "A13",
	                                      "entityVersion": "A-8651",
	                                      "entityId": "A16",
	                                      "sortableIndex": 1610612735,
	                                      "entityType": "category"
                                          },
                                          {
	                                      "type": "OUTFLOW",
	                                      "name": "Serious Family Support",
	                                      "cachedBalance": 0,
	                                      "masterCategoryId": "A13",
	                                      "entityVersion": "A-10",
	                                      "entityId": "A17",
	                                      "sortableIndex": 1879048191,
	                                      "entityType": "category"
                                          },
                                          {
	                                      "type": "OUTFLOW",
	                                      "name": "Cimate Commitment",
	                                      "cachedBalance": 0,
	                                      "masterCategoryId": "A13",
	                                      "entityVersion": "U-15045",
	                                      "entityId": "AB48D14B-96C3-DB3B-B508-A8276D231F8F",
	                                      "sortableIndex": 2013265919,
	                                      "entityType": "category"
                                          },
                                          {
	                                      "type": "OUTFLOW",
	                                      "name": "Folk Legacy",
	                                      "cachedBalance": 0,
	                                      "masterCategoryId": "A13",
	                                      "entityVersion": "U-15616",
	                                      "entityId": "DCF9F1B2-1F79-456D-0F08-290A6D5B8CBA",
	                                      "sortableIndex": 2080374783,
	                                      "entityType": "category"
                                          }
                                      ],
                                      "entityVersion": "A-5005",
                                      "entityId": "A13",
                                      "expanded": True,
                                      "sortableIndex": 1879048191,
                                      "entityType": "masterCategory"
                                  },
                                  {
                                      "type": "OUTFLOW",
                                      "deleteable": True,
                                      "name": "Joy",
                                      "subCategories": [
                                          {
	                                      "type": "OUTFLOW",
	                                      "name": "His",
	                                      "cachedBalance": 0,
	                                      "masterCategoryId": "A18",
	                                      "entityVersion": "A-13",
	                                      "entityId": "A20",
	                                      "sortableIndex": 1073741823,
	                                      "entityType": "category"
                                          },
                                          {
	                                      "type": "OUTFLOW",
	                                      "name": "Hers",
	                                      "cachedBalance": 0,
	                                      "masterCategoryId": "A18",
	                                      "entityVersion": "A-14",
	                                      "entityId": "A21",
	                                      "sortableIndex": 1610612735,
	                                      "entityType": "category"
                                          },
                                          {
	                                      "type": "OUTFLOW",
	                                      "name": "Vacation",
	                                      "cachedBalance": 0,
	                                      "masterCategoryId": "A18",
	                                      "entityVersion": "A-15",
	                                      "entityId": "A22",
	                                      "sortableIndex": 1879048191,
	                                      "entityType": "category"
                                          },
                                          {
	                                      "type": "OUTFLOW",
	                                      "name": "Beer & Wine & Parties",
	                                      "cachedBalance": 0,
	                                      "masterCategoryId": "A18",
	                                      "entityVersion": "Q-8",
	                                      "entityId": "A23",
	                                      "sortableIndex": 2013265919,
	                                      "entityType": "category"
                                          },
                                          {
	                                      "type": "OUTFLOW",
	                                      "name": "Education",
	                                      "cachedBalance": 0,
	                                      "masterCategoryId": "A18",
	                                      "entityVersion": "A-17",
	                                      "entityId": "A24",
	                                      "sortableIndex": 2080374783,
	                                      "entityType": "category"
                                          },
                                          {
	                                      "type": "OUTFLOW",
	                                      "name": "Treats & Coffee",
	                                      "cachedBalance": 0,
	                                      "masterCategoryId": "A18",
	                                      "entityVersion": "U-16379",
	                                      "entityId": "A25",
	                                      "sortableIndex": 2113929215,
	                                      "entityType": "category"
                                          },
                                          {
	                                      "type": "OUTFLOW",
	                                      "name": "Magazines & Newspapers",
	                                      "cachedBalance": 0,
	                                      "masterCategoryId": "A18",
	                                      "entityVersion": "A-19",
	                                      "entityId": "A26",
	                                      "sortableIndex": 2130706431,
	                                      "entityType": "category"
                                          }
                                      ],
                                      "entityVersion": "A-5006",
                                      "entityId": "A18",
                                      "expanded": True,
                                      "sortableIndex": 2013265919,
                                      "entityType": "masterCategory"
                                  }]
        })

        o = OutputToSqlite(input, self.db_file)
        o.do_master_categories()
        assert(len(self.db['masterCategories']) == 2)
        assert(len(self.db['subCategories']) == 13)


    def test_monthly_budget(self):
        input = Object_recursive({"monthlyBudgets": [
	    {
		"month": "2014-02-01",
		"monthlySubCategoryBudgets": [
		    {
			"overspendingHandling": None,
			"parentMonthlyBudgetId": "MB/2014-02",
			"entityVersion": "A-77",
			"entityId": "MCB/2014-02/A18",
			"entityType": "monthlyCategoryBudget",
			"categoryId": "A18",
			"budgeted": 200
		    },
		    {
			"overspendingHandling": None,
			"parentMonthlyBudgetId": "MB/2014-02",
			"entityVersion": "A-78",
			"entityId": "MCB/2014-02/A16",
			"entityType": "monthlyCategoryBudget",
			"categoryId": "A16",
			"budgeted": 200
		    },
		    {
			"overspendingHandling": None,
			"parentMonthlyBudgetId": "MB/2014-02",
			"entityVersion": "A-79",
			"entityId": "MCB/2014-02/A17",
			"entityType": "monthlyCategoryBudget",
			"categoryId": "A17",
			"budgeted": 100
		    },
		    {
			"overspendingHandling": None,
			"parentMonthlyBudgetId": "MB/2014-02",
			"entityVersion": "A-80",
			"entityId": "MCB/2014-02/A24",
			"entityType": "monthlyCategoryBudget",
			"categoryId": "A24",
			"budgeted": 500
		    },
		    {
			"overspendingHandling": None,
			"parentMonthlyBudgetId": "MB/2014-02",
			"entityVersion": "A-81",
			"entityId": "MCB/2014-02/A25",
			"entityType": "monthlyCategoryBudget",
			"categoryId": "A25",
			"budgeted": 100
		    },
		    {
			"overspendingHandling": None,
			"parentMonthlyBudgetId": "MB/2014-02",
			"entityVersion": "A-82",
			"entityId": "MCB/2014-02/A26",
			"entityType": "monthlyCategoryBudget",
			"categoryId": "A26",
			"budgeted": 50
		    },
		    {
			"overspendingHandling": None,
			"parentMonthlyBudgetId": "MB/2014-02",
			"entityVersion": "A-83",
			"entityId": "MCB/2014-02/A27",
			"entityType": "monthlyCategoryBudget",
			"categoryId": "A27",
			"budgeted": 50
		    },
		    {
			"overspendingHandling": None,
			"parentMonthlyBudgetId": "MB/2014-02",
			"entityVersion": "A-84",
			"entityId": "MCB/2014-02/A28",
			"entityType": "monthlyCategoryBudget",
			"categoryId": "A28",
			"budgeted": 50
		    },
		    {
			"overspendingHandling": None,
			"parentMonthlyBudgetId": "MB/2014-02",
			"entityVersion": "A-85",
			"entityId": "MCB/2014-02/A29",
			"entityType": "monthlyCategoryBudget",
			"categoryId": "A29",
			"budgeted": 50
		    },
		    {
			"overspendingHandling": None,
			"parentMonthlyBudgetId": "MB/2014-02",
			"entityVersion": "A-86",
			"entityId": "MCB/2014-02/A30",
			"entityType": "monthlyCategoryBudget",
			"categoryId": "A30",
			"budgeted": 50
		    }
		],
		"entityVersion": "A-37",
		"entityId": "MB/2014-02",
		"entityType": "monthlyBudget"
	    },
	    {
		"month": "2014-01-01",
		"monthlySubCategoryBudgets": [],
		"entityVersion": "A-38",
		"entityId": "MB/2014-01",
		"entityType": "monthlyBudget"
	    },
	    {
		"month": "2013-12-01",
		"monthlySubCategoryBudgets": [],
		"entityVersion": "A-39",
		"entityId": "MB/2013-12",
		"entityType": "monthlyBudget"
	    }
	]})

        o = OutputToSqlite(input, self.db_file)
        o.do_monthly_budgets()
        assert(len(self.db['monthlyBudgets']) == 10)

if __name__ == '__main__':
    import sys
    pytest.main(args=sys.argv)
