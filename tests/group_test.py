from unittest import TestCase
from unittest.mock import patch, Mock
from decimal import Decimal

from finsim.group import Group
from test_data import generate_test_data

def generate_data_mock():
    data = generate_test_data()
    mock_data = Mock()
    mock_data.get_people.return_value = data['people']
    mock_data.get_shared_expenses.return_value = data['group']['expenses']
    return mock_data

def generate_person_mock(gross_salary='0', updated=False, total_saved='0'):
    mock_person = Mock()
    mock_person.payroll.gross = Decimal(gross_salary)
    mock_person.updated = updated
    mock_person.total_saved.return_value = Decimal(total_saved)
    return mock_person


@patch('finsim.group.Expenses')
@patch('finsim.group.Person')
class TestGroup(TestCase):

    def test_init(self, mock_person_init, mock_expenses_init):
        mock_data = generate_data_mock()
        mock_data.proportional_expenses = True
        group = Group(mock_data)
        
        mock_data.get_people.assert_called_once()
        mock_data.get_shared_expenses.assert_called_once()
        self.assertEqual(mock_person_init.call_count, 2)
        mock_expenses_init.assert_called_once()
        self.assertTrue(group.proportional_expenses)
        self.assertFalse(group.updated)

    def test_begin_year__proportional_expenses(self, mock_person_init, mock_expenses_init):
        mock_data = generate_data_mock()
        mock_data.proportional_expenses = True
        mock_person_1 = generate_person_mock(gross_salary='30000')
        mock_person_2 = generate_person_mock(gross_salary='20000')
        mock_person_init.side_effect = [ mock_person_1, mock_person_2 ]
        mock_expenses = Mock()
        mock_expenses.monthly_total = Decimal('1500')
        mock_expenses_init.return_value = mock_expenses
        group = Group(mock_data)

        group.begin_year()

        mock_person_1.begin_year.assert_called_with(joint_contrib=Decimal('900'))
        mock_person_2.begin_year.assert_called_with(joint_contrib=Decimal('600'))
        self.assertFalse(group.updated)

    def test_begin_year__even_expenses(self, mock_person_init, mock_expenses_init):
        mock_data = generate_data_mock()
        mock_data.proportional_expenses = False
        mock_person_1 = generate_person_mock(gross_salary='30000')
        mock_person_2 = generate_person_mock(gross_salary='20000')
        mock_person_init.side_effect = [ mock_person_1, mock_person_2 ]
        mock_expenses = Mock()
        mock_expenses.monthly_total = Decimal('1500')
        mock_expenses_init.return_value = mock_expenses
        group = Group(mock_data)

        group.begin_year()

        mock_person_1.begin_year.assert_called_with(joint_contrib=Decimal('750'))
        mock_person_2.begin_year.assert_called_with(joint_contrib=Decimal('750'))
        self.assertFalse(group.updated)

    def test_simulate_month(self, mock_person_init, _):
        mock_data = generate_data_mock()
        mock_person_1 = generate_person_mock(updated=False)
        mock_person_2 = generate_person_mock(updated=True)
        mock_person_init.side_effect = [ mock_person_1, mock_person_2 ]
        group = Group(mock_data)

        group.simulate_month()

        mock_person_1.simulate_month.assert_called_once()
        mock_person_2.simulate_month.assert_called_once()
        self.assertTrue(group.updated)

    def test_total_saved(self, mock_person_init, _):
        mock_data = generate_data_mock()
        mock_person_1 = generate_person_mock(total_saved='1500')
        mock_person_2 = generate_person_mock(total_saved='1000')
        mock_person_init.side_effect = [ mock_person_1, mock_person_2 ]
        group = Group(mock_data)

        result = group.total_saved()

        mock_person_1.total_saved.assert_called_once()
        mock_person_2.total_saved.assert_called_once()
        self.assertEqual(result, Decimal('2500'))

    def test_end_year(self, mock_person_init, mock_expenses_init):
        mock_data = generate_data_mock()
        mock_person_1 = generate_person_mock(total_saved='1500')
        mock_person_2 = generate_person_mock(total_saved='1000')
        mock_person_init.side_effect = [ mock_person_1, mock_person_2 ]
        mock_expenses = Mock()
        mock_expenses_init.return_value = mock_expenses
        group = Group(mock_data)

        result = group.end_year()

        mock_expenses.inflate.assert_called_once()
        mock_person_1.end_year.assert_called_once()
        mock_person_2.end_year.assert_called_once()

    def test_strategise(self, mock_person_init, _):
        mock_data = generate_data_mock()
        mock_person_1 = generate_person_mock(updated=False)
        mock_person_2 = generate_person_mock(updated=True)
        mock_person_init.side_effect = [ mock_person_1, mock_person_2 ]
        group = Group(mock_data)

        group.strategise()

        mock_person_1.strategise.assert_not_called()
        mock_person_2.strategise.assert_called_once()
        self.assertFalse(group.updated)
