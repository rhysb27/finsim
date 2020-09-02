from abc import ABC, abstractmethod
from decimal import Decimal as D

from finsim.utils import get_percentage_of, decimalise as D

class AccountGroup(ABC):
    def __init__(self, account_type, accounts_data):
        self.account_dict = {}
        for account in accounts_data:
            new_account = account_type(account_data=account)
            self.account_dict[account['name']] = new_account

    def apply_strategy(self, strategy):
        for name, payment in strategy.items():
            self.account_dict[name].payment_amount = payment

    def begin_year(self):
        for name, account in self.account_dict.items():
            account.begin_year()

    def end_year(self):
        for name, account in self.account_dict.items():
            account.end_year()

class Account(ABC):
    def __init__(self, account_data):
        self.name = account_data['name']
        self.interest_rate = D(account_data.get('interest_rate', 0))
        self.balance = D(account_data.get('starting_balance', 0))
        self.payment_amount = 0
        self.annual_report = self._init_report()
        self.overall_report = self._init_report()

    def begin_year(self):
        self.annual_report = self._init_report()

    def end_year(self):
        if self.interest_rate > 0:
            interest_amount = get_percentage_of(self.balance, self.interest_rate)
            self.balance += interest_amount
            self._update_reports('Interest', interest_amount)


    # -- Private Methods ----------------------------------

    def _init_report(self):
        report = {
            'Starting Balance': self.balance,
            'Payments / Deposits': 0
        }

        if self.interest_rate > 0:
            report['Interest'] = 0

        return report

    def _update_reports(self, key, amount):
        self.annual_report[key] += amount
        self.overall_report[key] += amount