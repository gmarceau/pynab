from utils import transaction_month, transactions_by_month, find
from jsobject import Object
from pprint import pprint

def walk_budget(budget, categoryId: str):
    """
      Walk all budget months
        If an amount is budgeted, add to running total
        Play all the transactions in that categoryId for that month
        If at the end the balance is negative:
          If overspendingHandling is 'Affectsbuffer, reset balance to 0
          If overspendingHandling is "Confined", keep balance

      Returns the state of the category across all month as an array
    """
    from collections import OrderedDict
    from itertools import groupby

    transactions = [t for t in budget.transactions
                    if is_transaction_touches_category(t, categoryId)]

    by_month = transactions_by_month(transactions)

    balance = 0.0
    overspendingHandling = 'AffectsBuffer'
    non_empty_budgets = [b for b in budget.monthlyBudgets if b.monthlySubCategoryBudgets]

    monthly_budgets = sorted(non_empty_budgets, key=lambda k: k.month)

    result = []
    for month_budget in monthly_budgets:
        year_month = month_budget.month[0:7]

        category_budget = find(lambda c: c.categoryId == categoryId, month_budget.monthlySubCategoryBudgets) or {}

        budgeted = category_budget.get('budgeted', 0)

        outflows = play_transactions(by_month.get(year_month, []), categoryId)

        balance = round(balance + budgeted + outflows, 2)

        overspendingHandling = category_budget.get('overspendingHandling') or overspendingHandling

        result_this_month = Object({
            'month': year_month,
            'entityType': 'monthlyEnvelopResult',
            'monthlySubCategoryBudgetsId': month_budget.entityId,
            'balance': balance,
            'outflows': outflows,
            'budgeted': budgeted,
            'overspendingHandling': overspendingHandling
        })

        if balance < 0 and overspendingHandling == 'AffectsBuffer':
            # Category is overspent for this month
            balance = 0

        result.append(result_this_month)

    return result


def is_transaction_touches_category(transaction, categoryId) -> bool:
    if transaction.categoryId == categoryId:
        return True

    if transaction.categoryId == "Category/__Split__":
        return any(sub.categoryId == categoryId
                   for sub in transaction.subTransactions)

    return False

def play_transactions(transactions, categoryId: str) -> float:
    """
    Play all the transactions in a categoryId
    split transactions. Return the total of those transactions.
    """
    balance = 0
    for transaction in transactions:
        if not is_transaction_touches_category(transaction, categoryId):
            continue

        if transaction.categoryId == categoryId:
            balance += transaction.amount
        else:
            for sub_transaction in transaction.subTransactions:
                if sub_transaction.categoryId == categoryId:
                    balance += sub_transaction.amount

    return balance

def play_monthly_transactions(budget, month, categoryId: str) -> float:
    """
    Play all the transactions in a categoryId for a month, including
    split transactions. Return the total of those transactions.
    """
    transactions_for_month = [t for t in budget.transactions
                              if transaction_month(t) == month]
    return play_transactions(transactions_for_month, categoryId)
