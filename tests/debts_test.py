from unittest import TestCase
from unittest.mock import patch, Mock
from decimal import Decimal

from finsim.debts import Debts, Debt

def generate_test_data():
    return [
        {
            'name': 'Loan from Friend',
            'starting_balance': '1000.00',
            'interest_rate': '0.00'
        },
        {
            'name': 'Credit Card',
            'starting_balance': '1500.00',
            'interest_rate': '10.00'
        }
    ]

@patch('finsim.debts.Debt')
class TestDebts(TestCase):

    def test_init(self, *_):
        test_data = generate_test_data()
        debt_group = Debts(test_data)
        self.assertListEqual(debt_group.recently_cleared, [])

    def test_pay(self, mock_debt_init):
        mock_loan = Mock()
        mock_loan.was_updated.return_value = False
        mock_credit = Mock()
        mock_credit.was_updated.return_value = True
        mock_debt_init.side_effect = [mock_loan, mock_credit]
        debt_group = Debts(generate_test_data())

        debt_group.pay()

        mock_loan.pay.assert_called_once()
        mock_loan.was_updated.assert_called_once()
        mock_credit.pay.assert_called_once()
        mock_loan.was_updated.assert_called_once()
        self.assertListEqual(debt_group.recently_cleared, ['Credit Card'])

    def test_reset_recently_cleared(self, *_):
        debt_group = Debts(generate_test_data())
        debt_group.recently_cleared = ['Credit Card']

        debt_group.reset_recently_cleared()

        self.assertListEqual(debt_group.recently_cleared, [])

    def test_to_list__active_only(self, mock_debt_init):
        mock_loan = Mock()
        mock_loan.active = True
        mock_credit = Mock()
        mock_credit.active = False
        mock_debt_init.side_effect = [mock_loan, mock_credit]
        debt_group = Debts(generate_test_data())

        result = debt_group.to_list(active_only=True)

    def test_to_list__all(self, mock_debt_init):
        mock_loan = Mock()
        mock_loan.active = True
        mock_credit = Mock()
        mock_credit.active = False
        mock_debt_init.side_effect = [mock_loan, mock_credit]
        debt_group = Debts(generate_test_data())

        result = debt_group.to_list(active_only=False)

        self.assertListEqual(result, [mock_loan, mock_credit])

    def test_to_string(self, mock_debt_init):
        test_data = generate_test_data()
        loan = Debt(test_data[0])
        credit = Debt(test_data[1])
        mock_debt_init.side_effect = [loan, credit]
        debt_group = Debts(test_data)

        result = debt_group.to_string()

        expected_string = (
            '\tLoan from Friend:  £1000\n' +
            '\tCredit Card:       £1500\n'
        )
        self.assertEqual(result, expected_string)

    def test_to_string__empty(self, mock_debt_init):
        test_data = generate_test_data()
        loan = Debt(test_data[0])
        loan.active = False
        credit = Debt(test_data[1])
        credit.active = False
        mock_debt_init.side_effect = [loan, credit]
        debt_group = Debts(test_data)

        result = debt_group.to_string()

        self.assertEqual(result, '')

class TestDebt(TestCase):

    def test_init(self):
        debt = Debt(generate_test_data()[0])
        self.assertEqual(debt.name, 'Loan from Friend')
        self.assertTrue(debt.active)
        self.assertFalse(debt.updated)

    def test_pay__active(self):
        debt = Debt(generate_test_data()[0])
        debt.payment_amount = Decimal('100')
        debt.pay()

        self.assertEqual(debt.balance, Decimal('900'))
        self.assertTrue(debt.active)
        self.assertFalse(debt.updated)
        self.assertEqual(debt.annual_report['Payments / Deposits'], Decimal('100'))
        self.assertEqual(debt.overall_report['Payments / Deposits'], Decimal('100'))

    def test_pay__clear_balance(self):
        debt = Debt(generate_test_data()[0])
        debt.payment_amount = Decimal('100')
        debt.balance = Decimal('100')
        debt.pay()

        self.assertEqual(debt.balance, Decimal('0'))
        self.assertFalse(debt.active)
        self.assertTrue(debt.updated)
        self.assertEqual(debt.annual_report['Payments / Deposits'], Decimal('100'))
        self.assertEqual(debt.overall_report['Payments / Deposits'], Decimal('100'))

    def test_pay__inactive(self):
        debt = Debt(generate_test_data()[0])
        debt.payment_amount = Decimal('100')
        debt.balance = Decimal('0')
        debt.active = False
        debt.pay()

        self.assertEqual(debt.balance, Decimal('0'))
        self.assertFalse(debt.active)
        self.assertFalse(debt.updated)
        self.assertEqual(debt.annual_report['Payments / Deposits'], Decimal('0'))
        self.assertEqual(debt.overall_report['Payments / Deposits'], Decimal('0'))

    def test_was_updated__true(self):
        debt = Debt(generate_test_data()[0])
        debt.updated = True
        result = debt.was_updated()

        self.assertTrue(result)
        self.assertFalse(debt.updated)

    def test_was_updated__false(self):
        debt = Debt(generate_test_data()[0])
        debt.updated = False
        result = debt.was_updated()

        self.assertFalse(result)
        self.assertFalse(debt.updated)
