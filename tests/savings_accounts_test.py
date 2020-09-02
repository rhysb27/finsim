from unittest import TestCase
from unittest.mock import patch, Mock
from decimal import Decimal

from finsim.savings_accounts import SavingsAccounts, SavingsAccount

def generate_test_data():
    return [
        {
            'name': 'Savings Acc.',
            'interest_rate': '1.00',
            'starting_balance': '0.00',
            'type': 'traditional'
        },
        {
            'name': 'Lifetime ISA',
            'interest_rate': '1.05',
            'starting_balance': '100.00',
            'type': 'lisa'
        }
    ]

@patch('finsim.savings_accounts.SavingsAccount')
class TestSavingsAccounts(TestCase):

    def test_init(self, mock_acc_init):
        test_data = generate_test_data()
        accounts = SavingsAccounts(test_data)
        self.assertEqual(mock_acc_init.call_count, 2)

    def test_pay(self, mock_debt_init):
        mock_traditional = Mock()
        mock_lisa = Mock()
        mock_debt_init.side_effect = [mock_traditional, mock_lisa]
        accounts = SavingsAccounts(generate_test_data())

        accounts.deposit()

        mock_traditional.deposit.assert_called_once()
        mock_lisa.deposit.assert_called_once()

    def test_total_saved(self, mock_debt_init):
        mock_traditional = Mock()
        mock_traditional.balance = Decimal('1000')
        mock_lisa = Mock()
        mock_lisa.balance = Decimal('1500')
        mock_debt_init.side_effect = [mock_traditional, mock_lisa]
        accounts = SavingsAccounts(generate_test_data())

        result = accounts.total_saved()
        self.assertEqual(result, Decimal('2500'))


class TestSavingsAccount(TestCase):

    def test_init__traditional(self):
        savings_acc = SavingsAccount(generate_test_data()[0])
        self.assertEqual(savings_acc.name, 'Savings Acc.')
        self.assertNotIn('Government Bonus', savings_acc.annual_report)
        self.assertNotIn('Government Bonus', savings_acc.overall_report)

    def test_init__lisa(self):
        savings_acc = SavingsAccount(generate_test_data()[1])
        self.assertEqual(savings_acc.name, 'Lifetime ISA')
        self.assertIn('Government Bonus', savings_acc.annual_report)
        self.assertIn('Government Bonus', savings_acc.overall_report)

    def test_deposit__traditional(self):
        savings_acc = SavingsAccount(generate_test_data()[0])
        savings_acc.payment_amount = Decimal('100')

        savings_acc.deposit()
        self.assertEqual(savings_acc.balance, Decimal('100'))
        self.assertEqual(savings_acc.annual_report['Payments / Deposits'], Decimal('100'))
        self.assertEqual(savings_acc.overall_report['Payments / Deposits'], Decimal('100'))
        self.assertNotIn('Government Bonus', savings_acc.annual_report)
        self.assertNotIn('Government Bonus', savings_acc.overall_report)

    def test_deposit__lisa(self):
        savings_acc = SavingsAccount(generate_test_data()[1])
        savings_acc.payment_amount = Decimal('100')

        savings_acc.deposit()
        self.assertEqual(savings_acc.balance, Decimal('225'))
        self.assertEqual(savings_acc.annual_report['Payments / Deposits'], Decimal('100'))
        self.assertEqual(savings_acc.overall_report['Payments / Deposits'], Decimal('100'))
        self.assertEqual(savings_acc.annual_report['Government Bonus'], Decimal('25'))
        self.assertEqual(savings_acc.overall_report['Government Bonus'], Decimal('25'))
