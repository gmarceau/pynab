from jsobject import Object
from utils import groupby

def transaction_month(t):
    return t.date[0:7]

def transactions_by_month(transactions):
    from collections import OrderedDict

    return OrderedDict(groupby(sorted(transactions, key=lambda t: t.date),
                               key=transaction_month))

def transaction_touches_category(transaction, categoryId) -> bool:
    if transaction.categoryId == categoryId:
        return True

    if transaction.categoryId == "Category/__Split__":
        return any(sub.categoryId == categoryId
                   for sub in transaction.subTransactions)

    return False

def play_transaction(t, accountId=None, categoryId=None):
    print('--23', t)
    if accountId not in {None, t.get('accountId', accountId), t.get('targetAccountId')}:
        return 0
    print('--25')

    is_transfer = 'targetAccountId' in t
    is_backward = is_transfer and accountId and t.targetAccountId == accountId
    is_split = t.categoryId == "Category/__Split__"
    print('--30', is_transfer, is_backward, is_split)

    if is_transfer and not accountId:
        return 0
    print('--34')

    balance = 0
    if is_split:
        for sub_transaction in t.subTransactions:
            balance += play_transaction(sub_transaction, accountId, categoryId)
        print('--41', balance)

    elif not categoryId or categoryId == t.categoryId:
        balance = t.amount
        print('--45', balance)

    if is_backward:
        balance = -balance
    print('--49', balance)

    return balance


def play_transactions(transactions, accountId=None, categoryId=None, decorate=False, starting_balance=0):
    """
    Play all the transactions in a accountID, and in categoryId, respecting split transactions.

    If decorate is True, returns the list of transactions decorated with a running balance,
    starting with `starting_balance`
    """
    balance = starting_balance
    result = []

    for t in transactions:
        balance += play_transaction(t, accountId, categoryId)

        if decorate:
            with_balance = Object(t.copy())
            with_balance.balance = balance
            result.append(with_balance)

    if decorate:
        return result
    else:
        return balance

def play_transactions_category(transactions, categoryId: str) -> float:
    return play_transactions(transactions, categoryId=categoryId)

def play_monthly_transactions_category(budget, month, categoryId: str) -> float:
    """
    Play all the transactions in a categoryId for a month, including
    split transactions. Return the total of those transactions.
    """
    transactions_for_month = [t for t in budget.transactions
                              if transaction_month(t) == month]
    return play_transactions_category(transactions_for_month, categoryId)
