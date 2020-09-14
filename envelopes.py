from jsobject import Object
from utils import find
from transactions import transactions_by_month
from transactions import play_transactions_category, transaction_touches_category

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
    transactions = [t for t in budget.transactions
                    if transaction_touches_category(t, categoryId)]

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

        outflows = play_transactions_category(by_month.get(year_month, []), categoryId)

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
