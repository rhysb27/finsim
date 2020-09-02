from finsim.utils import get_percentage_of, round_currency, decimalise as D
from finsim.sim_data import INFLATION_RATE

class Expenses:

    def __init__(self, expenses_data):
        self.monthly_expenses = [ Expense(e) for e in expenses_data.get('monthly', []) ]
        self.annual_expenses = [ Expense(e) for e in expenses_data.get('annual', []) ]
        self._calculate_monthly_total()

    def inflate(self):
        for expense in (self.monthly_expenses + self.annual_expenses):
            expense.inflate()
        self._calculate_monthly_total()


    # -- Private Methods ----------------------------------

    def _calculate_monthly_total(self):
        monthly_sum = sum([e.cost for e in self.monthly_expenses])
        annual_sum = sum([e.cost for e in self.annual_expenses])
        annual_per_month = round_currency( annual_sum / D('12'), round_up=True )
        self.monthly_total = monthly_sum + annual_per_month


class Expense:
    def __init__(self, expense_data):
        self.name = expense_data['name']
        self.cost = D(expense_data['cost'])
        self.inflation = expense_data.get('inflation', True)

    def inflate(self):
        if self.inflation:
            inflation_amount = get_percentage_of(self.cost, INFLATION_RATE)
            self.cost += inflation_amount
