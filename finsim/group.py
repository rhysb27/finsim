from finsim.expenses import Expenses
from finsim.person import Person
from finsim.utils import get_percentage_of, round_currency

class Group:
    def __init__(self, data):
        people_data = data.get_people()
        self.people = [Person(person) for person in people_data]
        self.expenses = Expenses(data.get_shared_expenses())
        self.proportional_expenses = data.proportional_expenses
        self.updated = False

    def begin_year(self):
        monthly_expense_total = self.expenses.monthly_total
        if self.proportional_expenses:
            combined_salaries = sum([person.payroll.gross for person in self.people])
            for person in self.people:
                contrib_ratio = (person.payroll.gross / combined_salaries) * 100
                contrib = get_percentage_of(monthly_expense_total, contrib_ratio, round_up=True)
                person.begin_year(joint_contrib=contrib)
        else:
            num_people = len(self.people)
            for person in self.people:
                contrib = round_currency(monthly_expense_total / num_people, round_up=True)
                person.begin_year(joint_contrib=contrib)
        
        self.updated = False

    def simulate_month(self):
        for person in self.people:
            person.simulate_month()
            if person.updated:
                self.updated = True
        
    def total_saved(self):
        return sum([person.total_saved() for person in self.people])

    def end_year(self):
        self.expenses.inflate()
        for person in self.people:
            person.end_year()

    def strategise(self):
        for person in self.people:
            if person.updated:
                person.strategise()
        self.updated = False
