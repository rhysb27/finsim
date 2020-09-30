from unittest import TestCase
from unittest.mock import patch, Mock, ANY
from decimal import Decimal

from finsim.ui import UI, UserRequestedRestart

@patch('builtins.print')
class TestUI(TestCase):

    # -- Basic Output Functions -------------------------------------

    @patch('finsim.ui.UI._heading', return_value='Test')
    def test_initialise(self, mock_heading, _):
        UI.initialise()
        mock_heading.assert_called_once_with(ANY, level=2)
        
    @patch('finsim.ui.UI._heading', return_value='Test')
    def test_begin(self, mock_heading, _):
        UI.begin()
        mock_heading.assert_called_once_with(ANY, level=1)
        
    @patch('finsim.ui.UI._heading', return_value='Test')
    def test_cancel(self, mock_heading, _):
        UI.cancel()
        mock_heading.assert_called_once_with(ANY, level=1)
        
    @patch('finsim.ui.UI._heading', return_value='Test')
    def test_end_year(self, mock_heading, mock_print):
        mock_model = Mock()
        mock_model.total_saved.return_value = Decimal('1500')

        UI.end_year(mock_model, year=3)

        mock_heading.assert_called_once_with('END OF YEAR 3', level=2)
        mock_print.assert_any_call('Total saved to date: £1500')

    @patch('finsim.ui.UI._heading', return_value='Test')
    def test_end__pluaral_labels(self, mock_heading, mock_print):
        UI.end(total_months=27)
        mock_heading.assert_called_once_with(ANY, level=1)
        mock_print.assert_any_call('Goal achieved in 2 years and 3 months.\n')

    @patch('finsim.ui.UI._heading', return_value='Test')
    def test_end__singular_labels(self, mock_heading, mock_print):
        UI.end(total_months=13)
        mock_heading.assert_called_once_with(ANY, level=1)
        mock_print.assert_any_call('Goal achieved in 1 year and 1 month.\n')

    # -- Initialisation Functions -----------------------------------
    
    @patch('finsim.ui.UI._err')
    @patch('builtins.input')
    def test_obtain_savings_goal__happy_path(self, mock_input, mock_err, _):
        mock_input.return_value = '10000'
        result = UI.obtain_savings_goal()

        mock_input.assert_called_once()
        mock_err.assert_not_called()
        self.assertEqual(result, Decimal('10000'))

    @patch('finsim.ui.UI.cancel')
    @patch('builtins.input')
    def test_obtain_savings_goal__exit(self, mock_input, mock_cancel, _):
        mock_input.return_value = 'Q'
        with self.assertRaises(SystemExit):
            UI.obtain_savings_goal()

        mock_input.assert_called_once()
        mock_cancel.assert_called_once()
    
    @patch('finsim.ui.UI._err')
    @patch('builtins.input')
    def test_obtain_savings_goal__invalid(self, mock_input, mock_err, _):
        mock_input.side_effect = ['LOTS OF MONEY', '10000']
        UI.obtain_savings_goal()

        self.assertEqual(mock_input.call_count, 2)
        mock_err.assert_called_once_with('Please input a valid number or keyboard command.')
    
    @patch('finsim.ui.UI._err')
    @patch('builtins.input')
    def test_obtain_savings_goal__negative(self, mock_input, mock_err, _):
        mock_input.side_effect = ['-10000', '10000']
        UI.obtain_savings_goal()

        self.assertEqual(mock_input.call_count, 2)
        mock_err.assert_called_once_with('Please enter a savings goal greater than 0.')


    # -- Strategy Functions -----------------------------------------

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
    def test_obtain_initial_strategy__multiple_attempts(self, mock_prepare, mock_strategy, mock_heading, _):
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
    def test_obtain_new_strategy__happy_path(self, mock_prepare, mock_hint, mock_summary, mock_strategy, _):
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
    def test_obtain_new_strategy__multiple_attempts(self, mock_prepare, mock_hint, mock_summary, mock_strategy, mock_heading, _):
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

    def test_prepare_data_for_strategy(self, _):
        self.assertFalse(True)

