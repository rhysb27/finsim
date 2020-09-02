from decimal import Decimal as D

from finsim.accounts import AccountGroup, Account
from finsim.utils import get_percentage_of

class SavingsAccounts(AccountGroup):
    def __init__(self, accounts_data):
        super().__init__(SavingsAccount, accounts_data)

    def deposit(self):
        for name, account in self.account_dict.items():
            account.deposit()

    def total_saved(self):
        return sum([v.balance for k, v in self.account_dict.items()])


class SavingsAccount(Account):
    def __init__(self, account_data):
        self.type = account_data.get('type', 'traditional')
        super().__init__(account_data)

    def deposit(self):
        if self.type == 'lisa':
            gov_bonus = get_percentage_of(self.payment_amount, D('25'))
            self.balance += gov_bonus
            self._update_reports('Government Bonus', gov_bonus)

        self.balance += self.payment_amount
        self._update_reports('Payments / Deposits', self.payment_amount)


    # -- Private Methods ----------------------------------

    def _init_report(self):
        report = super()._init_report()
        
        if self.type == 'lisa':
            report['Government Bonus'] = D('0')

        return report
