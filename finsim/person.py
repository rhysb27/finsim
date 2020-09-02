from finsim import ui
from finsim.debts import Debts
from finsim.expenses import Expenses
from finsim.payroll import Payroll
from finsim.savings_accounts import SavingsAccounts


class Person:
    def __init__(self, person_data):
        self.name = person_data['name']
        self.payroll = Payroll(person_data['salary'])
        self.expenses = Expenses(person_data['expenses'])
        self.savings_accounts = SavingsAccounts(person_data['savings'])
        self.debts = Debts(person_data['debts'])

        self.joint_contrib = None
        self.disposable_income = None
        self.current_strategy = None
        self.outdated_strategies = []
        self.updated = False

    def begin_year(self, joint_contrib=0):
        self.joint_contrib = joint_contrib
        total_expenses = self.expenses.monthly_total + joint_contrib
        self.disposable_income = self.payroll.net_monthly - total_expenses
        self.strategise()

    def strategise(self):
        if self.current_strategy is None:
            new_strategy = ui.obtain_initial_strategy(self)
        else:
            new_strategy = ui.obtain_new_strategy(self)
            self.outdated_strategies.append(self.current_strategy)
        
        self.current_strategy = new_strategy
        self.savings_accounts.apply_strategy(new_strategy['savings'])
        self.debts.apply_strategy(new_strategy['debts'])
        self.debts.reset_recently_cleared()
        self.updated = False

    def simulate_month(self):
        self.debts.pay()
        self.savings_accounts.deposit()
        if len(self.debts.recently_cleared) > 0:
            self.updated = True

    def total_saved(self):
        return self.savings_accounts.total_saved()

    def end_year(self):
        self.payroll.payrise()
        self.expenses.inflate()
        self.debts.end_year()
        self.savings_accounts.end_year()
