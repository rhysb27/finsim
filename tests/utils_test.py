from unittest import TestCase
from unittest.mock import patch, Mock
from decimal import Decimal

from finsim import utils

class TestUtils(TestCase):

    def test_decimalise(self):
        result = utils.decimalise(10)
        self.assertIsInstance(result, Decimal)
        self.assertEqual(result, Decimal('10'))

    def test_round_currency__round_up(self):
        result = utils.round_currency(Decimal('10.001'), round_up=True)
        self.assertEqual(result, Decimal('10.01'))

    def test_round_currency__round_down(self):
        result = utils.round_currency(Decimal('10.001'), round_up=False)
        self.assertEqual(result, Decimal('10.00'))

    def test_round_currency_to_pounds__round_up(self):
        result = utils.round_currency_to_pounds(Decimal('10.50'), round_up=True)
        self.assertEqual(result, Decimal('11'))

    def test_round_currency_to_pounds__round_down(self):
        result = utils.round_currency_to_pounds(Decimal('10.50'), round_up=False)
        self.assertEqual(result, Decimal('10'))

    def test_get_percentage_of(self):
        result = utils.get_percentage_of(Decimal('50'), Decimal('10'))
        self.assertEqual(result, Decimal('5'))
