from unittest import TestCase
from unittest.mock import patch, Mock
from decimal import Decimal
from os import environ

from finsim.payroll import Payroll

def generate_test_data():
    return {
        'base_salary': '20000',
        'pension': '4.0',
        'payrise_rate': '5.0'
    }

class TestPayroll(TestCase):

    @patch('finsim.payroll.Payroll._calculate_net_salary')
    def test_init(self, mock_calculate):
        payroll = Payroll(generate_test_data())

        self.assertIsInstance(payroll.gross, Decimal)
        self.assertEqual(payroll.gross, Decimal('20000'))
        self.assertIsInstance(payroll.pension_rate, Decimal)
        self.assertEqual(payroll.pension_rate, Decimal('4.0'))
        self.assertIsInstance(payroll.payrise_rate, Decimal)
        self.assertEqual(payroll.payrise_rate, Decimal('5.0'))
        mock_calculate.assert_called_once()

    @patch('finsim.payroll.Payroll._calculate_net_salary')
    def test_payrise(self, mock_calculate):
        payroll = Payroll(generate_test_data())
        payroll.payrise()       

        self.assertIsInstance(payroll.gross, Decimal)
        self.assertEqual(payroll.gross, Decimal('21000'))
        self.assertEqual(mock_calculate.call_count, 2)

    @patch('finsim.payroll.data')
    def test_calculate_net_salary(self, mock_data):
        mock_data.INFLATION_RATE = Decimal('1')
        mock_data.NI_THRESHOLD = Decimal('10000')
        mock_data.NI_RATE = Decimal('10')
        mock_data.IT_THRESHOLD = Decimal('12500')
        mock_data.IT_RATE = Decimal('20')
        mock_data.SL_THRESHOLD = Decimal('25000')
        mock_data.SL_RATE = Decimal('10')
        payroll = Payroll(generate_test_data())

        self.assertIsInstance(payroll.net_monthly, Decimal)
        self.assertEqual(payroll.net_monthly, Decimal('1460'))
