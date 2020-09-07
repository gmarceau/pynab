from pprint import pprint
from json_objects import Object



non_liquidable_keywords = ['Mortgage', 'LineofCredit', 'CreditCard',
                           'MerchantAccount', 'OtherLiability',
                           'HSA', 'FSA', 'Equity', '401k', 'IRA']

non_liquid_account_keywords = non_liquidable_keywords + \
                              ['InvestmentAccount', 'OtherAsset', 'Investment', 'Retirement']

def liquid_position(budget, account_filter_keywords=None):
    import re
    from collections import OrderedDict
    from utils import transactions_by_month
    from itertools import dropwhile

    if not account_filter_keywords:
        account_filter_keywords = non_liquid_account_keywords

    account_filter_re = '|'.join("({})".format(item) for item in account_filter_keywords)

    def is_relevant_account(account):
        return not account.hidden and \
            not re.search(account_filter_re, account.accountName) and \
            not re.search(account_filter_re, account.accountType)

    relevant_accounts = {acc.entityId for acc in budget.accounts if is_relevant_account(acc)}
    pprint([acc.lookup().accountName for acc in relevant_accounts])

    months = sorted([mb.month[0:7] for mb in budget.monthlyBudgets])
    txs_by_months = transactions_by_month(budget.transactions)

    result = OrderedDict({m: Object() for m in months})

    for acc in relevant_accounts:
        balance = 0
        for month in months:
            this_month = [tx for tx in txs_by_months.get(month, [])
                          if tx.accountId == acc]

            sum_this_month = sum([tx.amount for tx in this_month])
            balance = balance + sum_this_month
            result[month][acc.lookup().accountName] = balance

    for month_result in result.values():
        month_result['total'] = sum(month_result.values())

    return OrderedDict(dropwhile(lambda m: m[1].total == 0, result.items()))
