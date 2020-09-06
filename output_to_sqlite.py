import dataset
from jsobject import Object

class OutputToSqlite:
    def __init__(self, budget, out_file):
        self.budget = budget
        if out_file.exists():
            out_file.delete()
        self.db = dataset.connect('sqlite:///{}'.format(out_file))

    def do_json_item(self, table_name):
        with self.db as tx:
            table = self.db[table_name]
            table.insert(self.budget[table_name])

    def do_json_array(self, table_name):
        with self.db as tx:
            table = self.db[table_name]
            # table.insert_many(self.budget[table_name])
            for item in self.budget[table_name]:
                table.insert(item)

    def do_payees(self):
        rename_conditions_table = self.db['payeesRenameConditions']
        locations_table = self.db['locations']
        payees_table = self.db['payees']
        with self.db as tx:
            for p in self.budget.payees:
                result = p.copy()
                if 'renameConditions' in p:
                    rename_conditions_table.insert_many(p.renameConditions or [])
                    result.pop('renameConditions')

                if 'locations' in p:
                    locations_table.insert_many(p.locations or [])
                    result.pop('locations')

                payees_table.insert(result)

    def do_scheduled_transactions(self):
        scheduled_transactions_table = self.db['scheduledTransactions']
        sub_transactions_table = self.db['subTransactions']

        with self.db as tx:
            for item in self.budget.scheduledTransactions:
                result = item.copy()
                if 'subTransactions' in item:
                    sub_transactions_table.insert_many(item.subTransactions or [])
                    result.pop('subTransactions')

                scheduled_transactions_table.insert(result)



    def do_transaction(self, item):
        result = Object(item.copy())
        result.has_subtransactions = False
        sub_transactions = []

        if 'subTransactions' in item:
            result.has_subtransactions = bool(item.subTransactions)
            sub_transactions = item.subTransactions
            result.pop('subTransactions')

        if 'matchedTransactions' in item:
            result.pop('matchedTransactions')

        self.transactions_table.insert(result)
        for sub in sub_transactions:
            self.sub_transactions_table.insert(sub)

    def do_transactions(self):
        with self.db as tx:
            self.transactions_table = self.db['transactions']
            self.sub_transactions_table = self.db['subTransactions']

            for item in self.budget.transactions:
                self.do_transaction(item)

    def do_master_category(self, master_category):
        sub_categories = master_category.subCategories
        master_result = master_category.copy()
        master_result.pop('subCategories')
        self.master_categories_table.insert(master_result)

        for sub in sub_categories or []:
            self.sub_categories_table.insert(sub)

    def do_master_categories(self):
        with self.db as tx:
            self.master_categories_table = self.db['masterCategories']
            self.sub_categories_table = self.db['subCategories']
            for c in self.budget.masterCategories:
                self.do_master_category(c)

    def do_monthly_budgets(self):
        self.monthly_budgets_table = self.db['monthlyBudgets']
        with self.db as tx:
            for month_entry in self.budget.monthlyBudgets:
                month = month_entry.month
                for budget_entry in month_entry.monthlySubCategoryBudgets:
                    result = budget_entry.copy()
                    result['month'] = month
                    self.monthly_budgets_table.insert(result)

    def do(self):
        with self.db as tx:
            self.do_payees()
            self.do_json_item('budgetMetaData')
            self.do_json_array('accounts')
            self.do_json_item('fileMetaData')
            self.do_scheduled_transactions()
            self.do_transactions()
            self.do_master_categories()
            self.do_monthly_budgets()


def do(budget, out_file):
    return OutputToSqlite(budget, out_file).do()
