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
from forbiddenfruit import curse

import output_to_sqlite
from json_objects import json_load_js_style

def find_full_budget(path):
    """
    Given a path (to a YNAB budget bundle) load the meta data and try to
    find a datafile with full knowledge we can work from.
    """
    info = json_load_js_style(path / "Budget.ymeta")

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

def create_index(data):
    result = {}

    def recur(item):
        if isinstance(item, dict):
            if 'entityId' in item:
                result[item.entityId] = item
            for v in item.values():
                recur(v)
        elif isinstance(item, list):
            for v in item:
                recur(v)

    recur(data)
    return result


top_budget = None
def lookup_entity_id(self):
    return top_budget.index[self]
curse(str, "lookup", lookup_entity_id)



def load_budget(path):
    global top_budget

    if path.is_dir():
        path = find_full_budget(path)

    if not path or not path.exists():
        raise(Exception("Unable to guess budget location"))

    data =  json_load_js_style(path)
    data['index'] = create_index(data)
    top_budget = data
    return(data)


def last_month_envelopes(budget):
    from envelopes import walk_budget
    from utils import sub_category_is_dead, sub_category_sort_index

    ids = [c.entityId for mc in budget.masterCategories for c in mc.subCategories or []]
    ids = [i for i in ids if not sub_category_is_dead(i)]

    envelop_results = {cId: walk_budget(budget, cId) for cId in ids}


    envelop_results_sorted = sorted([(k, v[-2]) for k, v in envelop_results.items()],
                                    key=lambda p: sub_category_sort_index(p[0]))
    with_names = [(k.lookup().name, v) for k, v in envelop_results_sorted]
    return with_names

class YnabParse(cli.Application):



    @cli.switch('--loglevel', argtype=str, help='set the log level')
    def log_level(self, level):
        logConfigArgs = dict()
        numeric_level = getattr(logging, level.upper(), None)
        # Double-check it's a valid logging level
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % level)
        logging.basicConfig(level=numeric_level)

    output_sqlite = cli.SwitchAttr('--to-sqlite', argtype=local.path, help='Convert budget to sqlite')
    repl = cli.Flag('--repl')

    @cli.positional(local.path)
    def main(self, path):  # pylint: disable=arguments-differ
        budget = load_budget(path)

        if self.output_sqlite:
            output_to_sqlite.do(budget, self.output_sqlite)
        else:
            from envelopes import walk_budget
            pprint(last_month_envelopes(budget))
            # pprint(walk_budget(budget, 'A69'))

        if self.repl:
            from ptpython.repl import embed
            embed(globals(), locals())



if __name__ == '__main__':
    YnabParse.run()
