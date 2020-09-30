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
class TestAccounts(TestCase):

    def test_init(self, mock_account_init):
        mock_account = mock_account_init.return_value
        test_data = generate_test_data()

        debt_group = Debts(test_data)

        self.assertEqual(len(debt_group.account_dict), 2)
        self.assertDictEqual(debt_group.account_dict, {
            'Loan from Friend': mock_account,
            'Credit Card': mock_account
        })
        mock_account_init.assert_any_call(account_data=test_data[0])
        mock_account_init.assert_any_call(account_data=test_data[1])
        self.assertEqual(mock_account_init.call_count, 2)

    def test_apply_strategy(self, mock_account_init):
        mock_loan = Mock()
        mock_credit = Mock()
        mock_account_init.side_effect = [mock_loan, mock_credit]
        test_strategy = [
            { 'name': 'Loan from Friend', 'payment': Decimal('100') },
            { 'name': 'Credit Card',      'payment': Decimal('125') }
        ]

        debt_group = Debts(generate_test_data())
        debt_group.apply_strategy(test_strategy)

        self.assertEqual(mock_loan.payment_amount, Decimal('100'))
        self.assertEqual(mock_credit.payment_amount, Decimal('125'))

    def test_begin_year(self, mock_account_init):
        mock_loan = Mock()
        mock_credit = Mock()
        mock_account_init.side_effect = [mock_loan, mock_credit]

        debt_group = Debts(generate_test_data())
        debt_group.begin_year()

        mock_loan.begin_year.assert_called_once()
        mock_credit.begin_year.assert_called_once()

    def test_end_year(self, mock_account_init):
        mock_loan = Mock()
        mock_credit = Mock()
        mock_account_init.side_effect = [mock_loan, mock_credit]

        debt_group = Debts(generate_test_data())
        debt_group.end_year()

        mock_loan.end_year.assert_called_once()
        mock_credit.end_year.assert_called_once()


class TestAccount(TestCase):

    def test_init__zero_interest(self):
        debt = Debt(generate_test_data()[0])
        self.assertEqual(debt.name, 'Loan from Friend')
        self.assertIsInstance(debt.interest_rate, Decimal)
        self.assertEqual(debt.interest_rate, Decimal('0'))
        self.assertIsInstance(debt.balance, Decimal)
        self.assertEqual(debt.balance, Decimal('1000'))
        self.assertEqual(debt.payment_amount, 0)
        self.assertNotIn('Interest', debt.annual_report)
        self.assertNotIn('Interest', debt.overall_report)

    def test_init__with_interest(self):
        debt = Debt(generate_test_data()[1])
        self.assertEqual(debt.name, 'Credit Card')
        self.assertIsInstance(debt.interest_rate, Decimal)
        self.assertEqual(debt.interest_rate, Decimal('10'))
        self.assertIsInstance(debt.balance, Decimal)
        self.assertEqual(debt.balance, Decimal('1500'))
        self.assertEqual(debt.payment_amount, 0)
        self.assertIn('Interest', debt.annual_report)
        self.assertIn('Interest', debt.overall_report)

    def test_begin_year(self):
        mock_report = { 'Payments / Deposits': Decimal('500') }
        debt = Debt(generate_test_data()[0])
        debt.annual_report = mock_report
        debt.overall_report = mock_report

        debt.begin_year()

        self.assertEqual(debt.overall_report['Payments / Deposits'], Decimal('500'))
        self.assertEqual(debt.annual_report['Payments / Deposits'], Decimal('0'))

    def test_end_year__zero_interest(self):
        debt = Debt(generate_test_data()[0])
        debt.end_year()

        self.assertNotIn('Interest', debt.annual_report)
        self.assertNotIn('Interest', debt.overall_report)
        self.assertEqual(debt.balance, Decimal('1000'))

    def test_end_year__with_interest(self):
        debt = Debt(generate_test_data()[1])
        debt.end_year()

        self.assertIn('Interest', debt.annual_report)
        self.assertIn('Interest', debt.overall_report)
        self.assertEqual(debt.annual_report['Interest'], Decimal('150'))
        self.assertEqual(debt.overall_report['Interest'], Decimal('150'))
        self.assertEqual(debt.balance, Decimal('1650'))
