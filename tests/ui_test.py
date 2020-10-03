from unittest import TestCase
from unittest.mock import patch, Mock, ANY
from decimal import Decimal

from finsim.ui import UI, UserRequestedRestart

class TestUI(TestCase):

    # -- Basic Output Functions -------------------------------------

    @patch('finsim.ui.UI._heading', return_value='Test')
    def test_initialise(self, mock_heading):
        UI.initialise()
        mock_heading.assert_called_once_with(ANY, level=2)
        
    @patch('finsim.ui.UI._heading', return_value='Test')
    def test_begin(self, mock_heading):
        UI.begin()
        mock_heading.assert_called_once_with(ANY, level=1)
        
    @patch('finsim.ui.UI._heading', return_value='Test')
    def test_cancel(self, mock_heading):
        UI.cancel()
        mock_heading.assert_called_once_with(ANY, level=1)
        
    @patch('builtins.print')
    @patch('finsim.ui.UI._heading', return_value='Test')
    def test_end_year(self, mock_heading, mock_print):
        mock_model = Mock()
        mock_model.total_saved.return_value = Decimal('1500')

        UI.end_year(mock_model, year=3)

        mock_heading.assert_called_once_with('END OF YEAR 3', level=2)
        mock_print.assert_any_call('Total saved to date: £1500')

    @patch('builtins.print')
    @patch('finsim.ui.UI._heading', return_value='Test')
    def test_end__pluaral_labels(self, mock_heading, mock_print):
        UI.end(total_months=27)
        mock_heading.assert_called_once_with(ANY, level=1)
        mock_print.assert_any_call('Goal achieved in 2 years and 3 months.\n')

    @patch('builtins.print')
    @patch('finsim.ui.UI._heading', return_value='Test')
    def test_end__singular_labels(self, mock_heading, mock_print):
        UI.end(total_months=13)
        mock_heading.assert_called_once_with(ANY, level=1)
        mock_print.assert_any_call('Goal achieved in 1 year and 1 month.\n')

    # -- Initialisation Functions -----------------------------------
    
    @patch('finsim.ui.UI._err')
    @patch('builtins.input')
    def test_obtain_savings_goal__happy_path(self, mock_input, mock_err):
        mock_input.return_value = '10000'
        result = UI.obtain_savings_goal()

        mock_input.assert_called_once()
        mock_err.assert_not_called()
        self.assertEqual(result, Decimal('10000'))

    @patch('finsim.ui.UI.cancel')
    @patch('builtins.input')
    def test_obtain_savings_goal__exit(self, mock_input, mock_cancel):
        mock_input.return_value = 'Q'
        with self.assertRaises(SystemExit):
            UI.obtain_savings_goal()

        mock_input.assert_called_once()
        mock_cancel.assert_called_once()
    
    @patch('finsim.ui.UI._err')
    @patch('builtins.input')
    def test_obtain_savings_goal__invalid(self, mock_input, mock_err):
        mock_input.side_effect = ['LOTS OF MONEY', '10000']
        UI.obtain_savings_goal()

        self.assertEqual(mock_input.call_count, 2)
        mock_err.assert_called_once_with('Please input a valid number or keyboard command.')
    
    @patch('finsim.ui.UI._err')
    @patch('builtins.input')
    def test_obtain_savings_goal__negative(self, mock_input, mock_err):
        mock_input.side_effect = ['-10000', '10000']
        UI.obtain_savings_goal()

        self.assertEqual(mock_input.call_count, 2)
        mock_err.assert_called_once_with('Please enter a savings goal greater than 0.')


    # -- Strategy Functions -----------------------------------------

    @patch('builtins.print')
    @patch('finsim.ui.UI._obtain_strategy', return_value={ 'TEST': 'test stuff '})
    @patch('finsim.ui.UI._summarise_strategy')
    @patch('finsim.ui.UI._new_strategy_hint')
    @patch('finsim.ui.UI._prepare_data_for_strategy')
    def test_obtain_initial_strategy__happy_path(self, mock_prepare, mock_hint, mock_summary, mock_strategy, mock_print):
        test_ui = UI()
        mock_person = Mock()
        mock_person.name = 'Joe'

        result = test_ui.obtain_initial_strategy(mock_person)

        self.assertDictEqual(result, { 'TEST': 'test stuff '})
        mock_prepare.assert_called_once_with(mock_person)
        mock_print.assert_any_call('Please provide an initial financial strategy for Joe.')
        mock_hint.assert_not_called()
        mock_summary.assert_not_called()
        mock_strategy.assert_called_once()

    @patch('finsim.ui.UI._heading', return_value='Test')
    @patch('finsim.ui.UI._obtain_strategy')
    @patch('finsim.ui.UI._prepare_data_for_strategy')
    def test_obtain_initial_strategy__multiple_attempts(self, mock_prepare, mock_strategy, mock_heading):
        test_ui = UI()
        mock_person = Mock()
        mock_person.name = 'Joe'
        mock_strategy.side_effect = [
            UserRequestedRestart(),
            UserRequestedRestart(),
            { 'TEST': 'test stuff '}
        ]

        result = test_ui.obtain_initial_strategy(mock_person)

        self.assertDictEqual(result, { 'TEST': 'test stuff '})
        self.assertEqual(mock_strategy.call_count, 3)
        mock_heading.assert_any_call('RESTARTING STRATEGY', level=3)

    @patch('finsim.ui.UI._obtain_strategy', return_value={ 'TEST': 'test stuff '})
    @patch('finsim.ui.UI._summarise_strategy')
    @patch('finsim.ui.UI._new_strategy_hint')
    @patch('finsim.ui.UI._prepare_data_for_strategy')
    def test_obtain_new_strategy__happy_path(self, mock_prepare, mock_hint, mock_summary, mock_strategy):
        test_ui = UI()
        mock_person = Mock()
        mock_person.name = 'Joe'
        mock_person.current_strategy = { 'Current Strategy': 'test data' }

        result = test_ui.obtain_new_strategy(mock_person)

        self.assertDictEqual(result, { 'TEST': 'test stuff '})
        mock_prepare.assert_called_once_with(mock_person)
        mock_hint.assert_called_once()
        mock_summary.assert_called_once_with({ 'Current Strategy': 'test data' })
        mock_strategy.assert_called_once()

    @patch('finsim.ui.UI._heading', return_value='Test')
    @patch('finsim.ui.UI._obtain_strategy')
    @patch('finsim.ui.UI._summarise_strategy')
    @patch('finsim.ui.UI._new_strategy_hint')
    @patch('finsim.ui.UI._prepare_data_for_strategy')
    def test_obtain_new_strategy__multiple_attempts(self, mock_prepare, mock_hint, mock_summary, mock_strategy, mock_heading):
        test_ui = UI()
        mock_person = Mock()
        mock_person.name = 'Joe'
        mock_strategy.side_effect = [
            UserRequestedRestart(),
            UserRequestedRestart(),
            { 'TEST': 'test stuff '}
        ]

        result = test_ui.obtain_new_strategy(mock_person)

        self.assertDictEqual(result, { 'TEST': 'test stuff '})
        self.assertEqual(mock_strategy.call_count, 3)
        mock_heading.assert_any_call('RESTARTING STRATEGY', level=3)


    # -- Strategy Helpers -------------------------------------------

    def test_prepare_data_for_strategy(self):
        mock_person = Mock()
        mock_person.disposable_income = Decimal('850.75')
        mock_debt_1 = Mock()
        mock_debt_2 = Mock()
        mock_debt_1.name = 'Credit Card'
        mock_debt_2.name = 'Car Loan'
        mock_person.debts.to_list.return_value = [ mock_debt_1, mock_debt_2 ]
        mock_savings_1 = Mock()
        mock_savings_2 = Mock()
        mock_savings_1.name = 'Lifetime ISA'
        mock_savings_2.name = 'Savings'
        mock_person.savings.to_list.return_value = [ mock_savings_1, mock_savings_2 ]

        test_ui = UI()
        test_ui._prepare_data_for_strategy(mock_person)

        self.assertEqual(test_ui.remaining_disposable, Decimal('850'))
        self.assertEqual(test_ui.acc_padding, 14)
        self.assertEqual(test_ui.rem_padding, 3)

    def test_new_strategy_hint__no_cleared(self):
        test_ui = UI()
        test_ui.recently_cleared = []
        mock_person = Mock()
        mock_person.name = 'Joe'
        test_ui.current_person = mock_person

        result = test_ui._new_strategy_hint()
        expected_hint = (
            'Please provide a new strategy for Joe.\n'
        )
        self.assertEqual(result, expected_hint)
    
    def test_new_strategy_hint__single_cleared(self):
        test_ui = UI()
        test_ui.recently_cleared = [ 'Credit Card' ]
        mock_person = Mock()
        mock_person.name = 'Joe'
        test_ui.current_person = mock_person

        result = test_ui._new_strategy_hint()
        expected_hint = (
            'Joe has paid off Credit Card. Please provide a new strategy for them.\n'
        )
        self.assertEqual(result, expected_hint)
    
    def test_new_strategy_hint__many_cleared(self):
        test_ui = UI()
        test_ui.recently_cleared = [ 'Credit Card', 'Car Loan', 'Overdraft' ]
        mock_person = Mock()
        mock_person.name = 'Joe'
        test_ui.current_person = mock_person

        result = test_ui._new_strategy_hint()
        expected_hint = (
            'Joe has paid off Credit Card, Car Loan and Overdraft. Please provide a new strategy for them.\n'
        )
        self.assertEqual(result, expected_hint)

    def test_summarise_strategy(self):
        test_ui = UI()
        test_ui.recently_cleared = [ 'Credit Card' ]
        test_ui.acc_padding = 13
        mock_strategy = {
            'debts': [
                { 'name': 'Credit Card', 'payment': Decimal('250') },
                { 'name': 'Car Loan', 'payment': Decimal('100') }
            ],
            'savings': [],
            'remaining': Decimal('150')
        }

        result = test_ui._summarise_strategy(mock_strategy)

        expected_summary = (
            '\tC̶r̶e̶d̶i̶t̶ ̶C̶a̶r̶d̶:̶ ̶ ̶£̶2̶5̶0̶\n' +
            '\tCar Loan:     £100\n' +
            '\t------------------\n' +
            '\tRemaining:    £150\n'
        )
        self.assertEqual(result, expected_summary)

    @patch('builtins.print')
    @patch('finsim.ui.UI._handle_confirmation')
    @patch('finsim.ui.UI._summarise_strategy')
    @patch('finsim.ui.UI._obtain_account_payments')
    def test_obtain_strategy__no_debts(self, mock_obtain, mock_summary, mock_confirm, mock_print):
        test_ui = UI()
        mock_person = Mock()
        mock_person.name = 'Joe'
        mock_savings = Mock()
        test_ui.current_person = mock_person
        test_ui.remaining_disposable = Decimal('1000')
        test_ui.debts = []
        test_ui.savings = mock_savings
        mock_obtain.return_value = [{ 'MOCK_STRATEGY': 'STUFF' }]

        result = test_ui._obtain_strategy()

        expected_strategy = {
            'savings': [{ 'MOCK_STRATEGY': 'STUFF' }],
            'remaining': Decimal('1000')
        }
        self.assertDictEqual(result, expected_strategy)
        mock_print.assert_any_call('Joe has ~£1000 disposable income per month.\n')
        mock_obtain.assert_called_once_with(mock_savings)
        mock_print.assert_any_call('\nThank you. Here’s a summary of Joe’s monthly strategy:\n')
        mock_summary.assert_called_once_with(expected_strategy)
        mock_confirm.assert_called_once()

    @patch('builtins.print')
    @patch('finsim.ui.UI._handle_confirmation')
    @patch('finsim.ui.UI._summarise_strategy')
    @patch('finsim.ui.UI._obtain_account_payments')
    def test_obtain_strategy__with_debts(self, mock_obtain, mock_summary, mock_confirm, mock_print):
        test_ui = UI()
        mock_person = Mock()
        mock_person.name = 'Joe'
        mock_savings = Mock()
        test_ui.current_person = mock_person
        test_ui.remaining_disposable = Decimal('1000')
        mock_debt_1 = Mock()
        mock_debt_2 = Mock()
        mock_debts = [ mock_debt_1, mock_debt_2 ]
        test_ui.debts = mock_debts
        test_ui.savings = mock_savings
        mock_obtain.return_value = [{ 'MOCK_STRATEGY': 'STUFF' }]

        result = test_ui._obtain_strategy()

        expected_strategy = {
            'debts': [{ 'MOCK_STRATEGY': 'STUFF' }],
            'savings': [{ 'MOCK_STRATEGY': 'STUFF' }],
            'remaining': Decimal('1000')
        }
        self.assertDictEqual(result, expected_strategy)
        mock_print.assert_any_call('Joe has ~£1000 disposable income per month and 2 debts:\n')
        mock_person.debts.to_string.assert_called_once()
        mock_obtain.assert_any_call(mock_debts)
        mock_obtain.assert_any_call(mock_savings)
        mock_print.assert_any_call('\nThank you. Here’s a summary of Joe’s monthly strategy:\n')
        mock_summary.assert_called_once_with(expected_strategy)
        mock_confirm.assert_called_once()

    @patch('finsim.ui.UI._handle_user_input')
    def test_obtain_account_payments(self, mock_input):
        test_ui = UI()
        test_ui.remaining_disposable = Decimal('1000')
        test_ui.rem_padding = 4
        test_ui.acc_padding = 13
        mock_acc_1 = Mock()
        mock_acc_2 = Mock()
        mock_acc_1.name = 'Credit Card'
        mock_acc_2.name = 'Car Loan'
        test_accounts = [ mock_acc_1, mock_acc_2 ]
        mock_input.side_effect = [ Decimal('100'), Decimal('250') ]
        
        result = test_ui._obtain_account_payments(test_accounts)

        mock_input.assert_any_call('\t[£1000 Remaining]    Credit Card:  £')
        mock_input.assert_any_call('\t[£900  Remaining]    Car Loan:     £')
        self.assertEqual(test_ui.remaining_disposable, Decimal('650'))
        expected_payments = [
            { 'name': 'Credit Card', 'payment': Decimal('100') },
            { 'name': 'Car Loan',    'payment': Decimal('250') }
        ]

    @patch('builtins.input')
    def test_handle_user_input__happy_path(self, mock_input):
        mock_prompt = 'Mock Prompt: £'
        mock_input.return_value = '250'
        test_ui = UI()
        test_ui.remaining_disposable = Decimal('1000')
        
        result = test_ui._handle_user_input(mock_prompt)

        self.assertEqual(result, Decimal('250'))
        mock_input.assert_called_once_with(mock_prompt)

    @patch('finsim.ui.UI.cancel')
    @patch('builtins.input')
    def test_handle_user_input__exit(self, mock_input, mock_cancel):
        mock_prompt = 'Mock Prompt: £'
        mock_input.return_value = 'Q'
        test_ui = UI()
        test_ui.remaining_disposable = Decimal('1000')
        
        with self.assertRaises(SystemExit):
            result = test_ui._handle_user_input(mock_prompt)

        mock_input.assert_called_once_with(mock_prompt)
        mock_cancel.assert_called_once()

    @patch('builtins.input')
    def test_handle_user_input__restart(self, mock_input):
        mock_prompt = 'Mock Prompt: £'
        mock_input.return_value = 'R'
        test_ui = UI()
        test_ui.remaining_disposable = Decimal('1000')
        
        with self.assertRaises(UserRequestedRestart):
            result = test_ui._handle_user_input(mock_prompt)

        mock_input.assert_called_once_with(mock_prompt)

    @patch('finsim.ui.UI._err')
    @patch('builtins.input')
    def test_handle_user_input__invalid_input(self, mock_input, mock_err):
        mock_prompt = 'Mock Prompt: £'
        mock_input.side_effect = [ 'all', '250' ]
        test_ui = UI()
        test_ui.remaining_disposable = Decimal('1000')
        
        result = test_ui._handle_user_input(mock_prompt)

        self.assertEqual(result, Decimal('250'))
        self.assertEqual(mock_input.call_count, 2)
        mock_input.assert_called_with(mock_prompt)
        expected_err = 'Please input a valid number or keyboard command.'
        mock_err.assert_called_with(expected_err)

    @patch('finsim.ui.UI._err')
    @patch('builtins.input')
    def test_handle_user_input__high_payment(self, mock_input, mock_err):
        mock_prompt = 'Mock Prompt: £'
        mock_input.side_effect = [ '1500', '250' ]
        test_ui = UI()
        test_ui.remaining_disposable = Decimal('1000')
        
        result = test_ui._handle_user_input(mock_prompt)

        self.assertEqual(result, Decimal('250'))
        self.assertEqual(mock_input.call_count, 2)
        mock_input.assert_called_with(mock_prompt)
        expected_err = 'Payment amount exceeds remaining disposable income. Please enter a valid value.'
        mock_err.assert_called_with(expected_err)

    @patch('finsim.ui.UI.cancel')
    @patch('builtins.input')
    def test_handle_confirmation__ok(self, mock_input, mock_cancel):
        mock_input.return_value = ''
        test_ui = UI()

        test_ui._handle_confirmation()
        mock_cancel.assert_not_called()

    @patch('finsim.ui.UI.cancel')
    @patch('builtins.input')
    def test_handle_confirmation__cancel(self, mock_input, mock_cancel):
        mock_input.return_value = 'Q'
        test_ui = UI()
        
        with self.assertRaises(SystemExit):
            test_ui._handle_confirmation()

        mock_cancel.assert_called_once()

    @patch('finsim.ui.UI.cancel')
    @patch('builtins.input')
    def test_handle_confirmation__restart(self, mock_input, mock_cancel):
        mock_input.return_value = 'R'
        test_ui = UI()
        
        with self.assertRaises(UserRequestedRestart):
            test_ui._handle_confirmation()

        mock_cancel.assert_not_called()


    # -- Formatters -------------------------------------------------

    def test_heading__level_1(self):
        result = UI._heading('TEST', level=1)
        expected_heading = (
            '\n\t====================================================' +
            '\n\t======================[ TEST ]======================' +
            '\n\t====================================================\n'
        )
        self.assertEqual(result, expected_heading)

    def test_heading__level_2(self):
        result = UI._heading('TEST', level=2)
        expected_heading = (
            '\n\t======================[ TEST ]======================\n'
        )
        self.assertEqual(result, expected_heading)

    def test_heading__level_3(self):
        result = UI._heading('TEST', level=3)
        expected_heading = (
            '\n\t----------------------[ TEST ]----------------------\n'
        )
        self.assertEqual(result, expected_heading)

    def test_strike(self):
        result = UI._strike('TEST')
        self.assertEqual(result, 'T̶E̶S̶T̶')

    def test_err(self):
        result = UI._err('TEST')
        expected_err = '\n[ ERROR ]: TEST\n'
        self.assertEqual(result, expected_err)

    def test_pad_name(self):
        test_ui = UI()
        test_ui.acc_padding = 8

        result = test_ui._pad_name('TEST')
        expected_result = 'TEST:   '
        self.assertEqual(result, expected_result)
