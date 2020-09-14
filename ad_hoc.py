from pprint import pprint
from json_objects import Object
from transactions import play_transactions, transaction_month
from utils import groupby

non_liquidable_keywords = ['Mortgage', 'LineofCredit', 'CreditCard',
                           'MerchantAccount', 'OtherLiability',
                           'HSA', 'FSA', 'Equity', '401k', 'IRA']

non_liquid_account_keywords = non_liquidable_keywords + \
                              ['InvestmentAccount', 'OtherAsset', 'Investment', 'Retirement']

def liquid_position(budget, account_filter_keywords=None):
    import re
    from collections import OrderedDict
    from transactions import transactions_by_month
    from itertools import dropwhile

    if not account_filter_keywords:
        account_filter_keywords = non_liquid_account_keywords

    account_filter_re = '|'.join("({})".format(item) for item in account_filter_keywords)

    def is_relevant_account(account):
        return not account.hidden and \
            not re.search(account_filter_re, account.accountName) and \
            not re.search(account_filter_re, account.accountType)

    relevant_accounts = {acc.entityId for acc in budget.accounts if is_relevant_account(acc)}

    by_account = {acc: txs for acc, txs in
                  groupby(budget.transactions, key=lambda t: t.accountId).items()
                  if acc in relevant_accounts}

    for acc, txs in by_account.items():
        by_account[acc] = play_transactions(txs, accountId=acc, decorate=True)

    months = sorted([mb.month[0:7] for mb in budget.monthlyBudgets])
    result = OrderedDict({m: Object() for m in months})

    for acc, txs in by_account.items():
        by_month = groupby(txs, key=transaction_month)
        balance = 0
        for month in months:
            if by_month.get(month):
                balance = by_month[month][-1].balance
            print('--46', month, balance, len(by_month.get(month, [])))

            pprint(by_month.get(month, []))
            result[month][acc.lookup().accountName] = balance

    for month_result in result.values():
        month_result['total'] = sum(month_result.values())

    return OrderedDict(dropwhile(lambda m: m[1].total == 0, result.items()))
