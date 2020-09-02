from decimal import Decimal as D

from finsim.accounts import AccountGroup, Account
from finsim.utils import get_percentage_of

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

    def get_active(self):
        return [d for k, d in self.account_dict.items() if d.active]

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