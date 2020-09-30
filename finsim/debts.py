from decimal import Decimal as D

from finsim.accounts import AccountGroup, Account
from finsim.utils import get_percentage_of, round_currency_to_pounds

class Debts(AccountGroup):
    def __init__(self, accounts_data):
        super().__init__(Debt, accounts_data)
        self.recently_cleared = []

    def pay(self):
        for name, debt in self.account_dict.items():
            debt.pay()
            cleared = debt.was_updated()
            if cleared: 
                self.recently_cleared.append(name)

    def reset_recently_cleared(self):
        self.recently_cleared = []

    def to_list(self, active_only=True):
        if active_only:
            return [ d for k, d in self.account_dict.items() if d.active ]
        else:
            return [ d for k, d in self.account_dict.items() ]

    def to_string(self):
        active_debts = [ d for _, d in self.account_dict.items() if d.active]
        if len(active_debts) == 0:
            return ''
        padding_length = max(len(d.name) for d in active_debts) + 2
        debt_string = ''
        for debt in active_debts:
            padded_name = '{}:'.format(debt.name).ljust(padding_length, ' ')
            debt_string += '\t{} £{}\n'.format(
                padded_name, 
                round_currency_to_pounds(debt.balance))

        return debt_string

class Debt(Account):
    def __init__(self, account_data):
        super().__init__(account_data) 
        self.active = self.balance > 0
        self.updated = False

    def pay(self):
        if self.active:
            self.balance -= self.payment_amount
            self._update_reports('Payments / Deposits', self.payment_amount)
            active = self.balance > 0
            self.updated = self.active != active
            self.active = active

    def was_updated(self):
        if self.updated:
            self.updated = False
            return True
        else:
            return False

    def end_year(self):
        if self.active:
            super().end_year()