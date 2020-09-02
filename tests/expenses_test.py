from unittest import TestCase
from unittest.mock import patch, Mock
from decimal import Decimal

from finsim.expenses import Expenses, Expense
from finsim.utils import get_percentage_of

def generate_test_data():
    return {
        'monthly': [
            { 'name': 'Groceries',     'cost': '500.00' },
            { 'name': 'Car Insurance', 'cost': '100.00' }
        ],
        'annual': [
            { 'name': 'Pet Insurance',   'cost': '80.00' },
            { 'name': 'Christmas Gifts', 'cost': '400.00', 'inflation': False }
        ]
    }

class TestExpenses(TestCase):
    
    def test_init(self):
        expenses = Expenses(generate_test_data())
        
        expected_total = 500 + 100 + ( (Decimal('80') + Decimal('400')) / 12)
        self.assertEqual(len(expenses.monthly_expenses), 2)
        self.assertEqual(len(expenses.annual_expenses), 2)
        self.assertEqual(expenses.monthly_total, expected_total)

    @patch('finsim.expenses.Expense')
    @patch('finsim.expenses.Expenses._calculate_monthly_total')
    def test_inflate(self, mock_recalculate, mock_expense_init):
        mock_expense = mock_expense_init.return_value
        expenses = Expenses(generate_test_data())
        expenses.inflate()

        self.assertEqual(mock_expense.inflate.call_count, 4)
        # Expecting calls for 1) Initialisation and 2) Post-inflation
        self.assertEqual(mock_recalculate.call_count, 2)

class TestExpense(TestCase):

    def test_init(self):
        test_data = generate_test_data()['annual'][0]
        expense = Expense(test_data)

        self.assertEqual(expense.name, 'Pet Insurance')
        self.assertIsInstance(expense.cost, Decimal)
        self.assertEqual(expense.cost, Decimal('80'))
        self.assertTrue(expense.inflation)

    @patch('finsim.expenses.INFLATION_RATE', Decimal('1'))
    def test_inflate(self):
        test_data = generate_test_data()['annual'][0]
        expense = Expense(test_data)
        expense.inflate()

        expected_new_cost = Decimal('80.80')
        self.assertEqual(expense.cost, expected_new_cost)

    def test_inflate__no_inflation(self):
        test_data = generate_test_data()['annual'][1]
        expense = Expense(test_data)
        expense.inflate()

        self.assertEqual(expense.cost, Decimal('400'))
