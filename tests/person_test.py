from unittest import TestCase
from unittest.mock import patch, Mock
from decimal import Decimal

from finsim.person import Person

def generate_test_data():
    from test_data import generate_test_data as gtd
    return gtd()['people'][0]

@patch('finsim.person.Debts')
@patch('finsim.person.SavingsAccounts')
@patch('finsim.person.Payroll')
@patch('finsim.person.Expenses')
class TestPerson(TestCase):

    def test_init(self, mock_expenses_init, mock_payroll_init, mock_savings_init, mock_debts_init):
        test_data = generate_test_data()
        person = Person(test_data)

        self.assertEqual(person.name, 'Alice')
        mock_payroll_init.assert_called_with(test_data['salary'])
        mock_expenses_init.assert_called_with(test_data['expenses'])
        mock_savings_init.assert_called_with(test_data['savings'])
        mock_debts_init.assert_called_with(test_data['debts'])

    @patch('finsim.person.Person.strategise')
    def test_begin_year(self, mock_strat, mock_expenses_init, mock_payroll_init, *_):
        mock_expenses = Mock()
        mock_expenses.monthly_total = Decimal('50')
        mock_expenses_init.return_value = mock_expenses
        mock_payroll = Mock()
        mock_payroll.net_monthly = Decimal('1500')
        mock_payroll_init.return_value = mock_payroll
        test_data = generate_test_data()
        person = Person(test_data)
        
        person.begin_year(joint_contrib=Decimal('1000'))

        self.assertEqual(person.joint_contrib, Decimal('1000'))
        self.assertEqual(person.disposable_income, Decimal('450'))
        mock_strat.assert_called_once()

    @patch('finsim.person.UI')
    def test_strategise__initial(self, mock_ui_init, *mocks):
        mock_strategy = {
            'savings': { 'MOCK ONE' },
            'debts': { 'MOCK TWO '} 
        }
        mock_ui = Mock()
        mock_ui.obtain_initial_strategy.return_value = mock_strategy
        mock_ui_init.return_value = mock_ui
        mock_savings = Mock()
        mock_savings_init = mocks[2]
        mock_savings_init.return_value = mock_savings
        mock_debts = Mock()
        mock_debts_init = mocks[3]
        mock_debts_init.return_value = mock_debts
        person = Person(generate_test_data())
        
        person.strategise()

        mock_ui.obtain_initial_strategy.assert_called_once()
        self.assertDictEqual(person.current_strategy, mock_strategy)
        self.assertListEqual(person.outdated_strategies, [])
        mock_savings.apply_strategy.assert_called_with(mock_strategy['savings'])
        mock_debts.apply_strategy.assert_called_with(mock_strategy['debts'])
        mock_debts.reset_recently_cleared.assert_called_once()
        self.assertFalse(person.updated)

    @patch('finsim.person.UI')
    def test_strategise__new(self, mock_ui_init, *mocks):
        mock_new_strategy = {
            'savings': { 'MOCK THREE' },
            'debts': { 'MOCK FOUR '} 
        }
        mock_current_strategy = {
            'savings': { 'MOCK ONE' },
            'debts': { 'MOCK TWO '} 
        }
        mock_ui = Mock()
        mock_ui.obtain_new_strategy.return_value = mock_new_strategy
        mock_ui_init.return_value = mock_ui
        mock_savings = Mock()
        mock_savings_init = mocks[2]
        mock_savings_init.return_value = mock_savings
        mock_debts = Mock()
        mock_debts_init = mocks[3]
        mock_debts_init.return_value = mock_debts
        person = Person(generate_test_data())
        person.current_strategy = mock_current_strategy
        
        person.strategise()

        mock_ui.obtain_new_strategy.assert_called_once()
        self.assertDictEqual(person.current_strategy, mock_new_strategy)
        self.assertListEqual(person.outdated_strategies, [mock_current_strategy])
        mock_savings.apply_strategy.assert_called_with(mock_new_strategy['savings'])
        mock_debts.apply_strategy.assert_called_with(mock_new_strategy['debts'])
        mock_debts.reset_recently_cleared.assert_called_once()
        self.assertFalse(person.updated)

    def test_simulate_month__updated(self, *mocks):
        mock_savings = Mock()
        mock_savings_init = mocks[2]
        mock_savings_init.return_value = mock_savings
        mock_debts = Mock()
        mock_debts.recently_cleared = [ 'Credit Card' ]
        mock_debts_init = mocks[3]
        mock_debts_init.return_value = mock_debts
        person = Person(generate_test_data())
        
        person.simulate_month()

        mock_debts.pay.assert_called_once()
        mock_savings.deposit.assert_called_once()
        self.assertTrue(person.updated)

    def test_simulate_month__not_updated(self, *mocks):
        mock_savings = Mock()
        mock_savings_init = mocks[2]
        mock_savings_init.return_value = mock_savings
        mock_debts = Mock()
        mock_debts.recently_cleared = []
        mock_debts_init = mocks[3]
        mock_debts_init.return_value = mock_debts
        person = Person(generate_test_data())
        
        person.simulate_month()

        mock_debts.pay.assert_called_once()
        mock_savings.deposit.assert_called_once()
        self.assertFalse(person.updated)

    def test_total_saved(self, *mocks):
        mock_savings = Mock()
        mock_savings.total_saved.return_value = Decimal('1500')
        mock_savings_init = mocks[2]
        mock_savings_init.return_value = mock_savings
        person = Person(generate_test_data())
        
        result = person.total_saved()

        self.assertEqual(result, Decimal('1500'))

    def test_end_year(self, mock_expenses_init, mock_payroll_init, mock_savings_init, mock_debts_init):
        mock_expenses = Mock()
        mock_expenses_init.return_value = mock_expenses
        mock_payroll = Mock()
        mock_payroll_init.return_value = mock_payroll
        mock_savings = Mock()
        mock_savings_init.return_value = mock_savings
        mock_debts = Mock()
        mock_debts_init.return_value = mock_debts
        person = Person(generate_test_data())

        person.end_year()

        mock_payroll.payrise.assert_called_once()
        mock_expenses.inflate.assert_called_once()
        mock_debts.end_year.assert_called_once()
        mock_savings.end_year.assert_called_once()



