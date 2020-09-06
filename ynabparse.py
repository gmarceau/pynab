#!/usr/bin/env python3
"""
Parse YNAB4's budget data to work out how much is left in the current month.

Written by James Seward 2013-07; http://jamesoff.net; @jamesoff
Thanks to @ppiixx for pointing out/fixing the rollover problem :)

BSD licenced, have fun.
"""

from typing import Union, Any, List, Optional, cast
import json
import datetime
import os.path
import locale
import sys
import argparse
import logging
from types import SimpleNamespace as Namespace
from pprint import pprint
from plumbum import cli, local # type: ignore

def new_walk_budget(data, category: str) -> float:
    """
    New algorithm:
      Walk all available months
        If an amount is budgeted, add to running total
        Play all the transactions in that category for that month
        If at the end the balance is negative:
          If overspendingHandling is null, reset balance to 0
          If overspendingHandling is "confined", keep balance
    """
    budget = 0.0
    saved_budget = None
    now = datetime.date.today()

    logging.debug("-- Starting walk_budget for %s" % category)

    monthly_budgets = sorted(data.monthlyBudgets, key=lambda k: k.month)
    saved_budget = 0.0

    for month in monthly_budgets:
        Y = int(month.month[0:4])
        M = int(month.month[5:7])
        budget_month = datetime.date(Y, M, 1)
        if budget_month > now:
            # Now we've reached the future so time to stop
            logging.debug("Reached the future")
            if not saved_budget == None and budget == 0:
                budget = saved_budget
            break
        logging.debug("")
        logging.debug("Starting %s with budget of %0.2f" % (month.month, budget))
        budget += get_monthly_budget(month.monthlySubCategoryBudgets, category)
        logging.debug("Budgeted amount for %s is %0.2f" %(month.month, budget))
        budget += play_monthly_transactions(data, month.month[0:7], category)
        logging.debug("Ended month with balance of %0.2f" % budget)
        if budget < 0:
            logging.debug("Category is overspent for this month!")
            osh = get_overspending_handling(month.monthlySubCategoryBudgets, category)

            if not osh == None and (not osh.lower() == "confined"):
                logging.debug("Resetting balance to 0")
                saved_budget = budget
                budget = 0

    logging.debug("Finished walking budget, balance is %0.2f" % budget)
    return budget


def play_monthly_transactions(data, month: str, categoryId: str) -> float:
    """
    Play all the transactions in a category for a month, including
    split transactions. Return the total of those transactions.
    """
    balance = 0
    found_data = False
    transactions = data.transactions
    for transaction in transactions:
        this_month = transaction.date[0:7]
        if this_month == month:
            if transaction.categoryId == "Category/__Split__":
                for sub_transaction in transaction.subTransactions:
                    if sub_transaction.categoryId == categoryId and not "isTombstone" in sub_transaction:
                        balance += sub_transaction.amount
                        logging.debug("  Found split transaction %s (%s)" % (sub_transaction.amount, balance))
            else:
                if transaction.categoryId == categoryId and not "isTombstone" in transaction:
                    balance += transaction.amount
                    logging.debug("  Found transaction %s (%s)" % (transaction.amount, balance))

    logging.debug("Monthly spend for this category is %0.2f" % balance)

    return balance


def get_monthly_budget(data, category):
    """
    Find the amount allocated to a category for a month.
    """
    return find_category(date, category).budgeted

def get_overspending_handling(data, category_name):
    """
    Find the overspendingHandling for a category in a month
    """
    c = find_category(date, category)
    return hasattr(c, "overspendingHandling") and c.overspendingHandling

def json_loads_with_namespace(filename):
    return json.loads(filename.read(), object_hook=lambda d: Namespace(**d))

def find_full_budget(path):
    """
    Given a path (to a YNAB budget bundle) load the meta data and try to
    find a datafile with full knowledge we can work from.
    """
    info = json_loads_with_namespace(path / "Budget.ymeta")

    folder_name = info.relativeDataFolderName

    # Now look in the devices folder, and find a folder which has full knowledge
    devices_path = path / folder_name / "devices"
    devices = devices_path.list()
    use_folder = ""

    for device in devices:
        device_info = json.loads((devices_path / device).read())
        if device_info.hasFullKnowledge:
            use_folder = device_info.deviceGUID
            break

    return path / folder_name / use_folder / "Budget.yfull"

def get_currency_symbol(data):
    """
    Try to guess the currency symbol for this budget file based on its
    locale.
    """
    currency_locale = data.budgetMetaData.currencyLocale
    locale.setlocale(locale.LC_ALL, locale.normalize(currency_locale))

def all_categories(data):
    """
    Find all the categories in a budget file, return as a dict by name
    """
    sub_categories = [sub_c for mc in data.masterCategories
                      if mc.name != "Hidden Categories"
                      for sub_c in mc.subCategories or []]
    return {sub_c.name: sub_c for sub_c in sub_categories
            if not (hasattr(sub_c, "isTombstone") and sub_c.isTombstone)}

def find_category(data, category_name: str) -> int:
    """
    Locate a particular category
    """
    return all_categories(data).get(category_name)

def load_budget(path):
    if path.is_dir():
        path = find_full_budget(path)

    if not path or not path.exists():
        raise(Exception("Unable to guess budget location"))

    return json_loads_with_namespace(path)


class YnabParse(cli.Application):

    @cli.switch('--loglevel', argtype=str, help='set the log level')
    def log_level(self, level):
        logConfigArgs = dict()
        numeric_level = getattr(logging, level.upper(), None)
        # Double-check it's a valid logging level
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % level)
        logging.basicConfig(level=numeric_level)

    @cli.positional(local.path)
    def main(self, path):  # pylint: disable=arguments-differ
        data = load_budget(path)
        logging.debug(find_category(data, "Clothing"))
        pprint(sorted(list(all_categories(data).keys())))


if __name__ == '__main__':
    YnabParse.run()
