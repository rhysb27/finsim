from unittest import TestCase
from unittest.mock import patch, Mock
from decimal import Decimal

from finsim.simulation import Simulation
from test_data import generate_test_data

def generate_data_mock(group_mode=True):
    data = generate_test_data()
    mock_data = Mock()
    mock_data.group_mode = group_mode
    if not group_mode:
        del data['people'][1]
        del data['group']

    mock_data.get_people.return_value = data['people']
   
    return mock_data

@patch('finsim.simulation.Person')
@patch('finsim.simulation.Group')
class TestSimulation(TestCase):

    def test_init__group_mode(self, mock_group_init, mock_person_init):
        mock_data = generate_data_mock(group_mode=True)
        simulation = Simulation(mock_data)

        self.assertTrue(simulation.group_mode)
        mock_group_init.assert_called_once()
        mock_person_init.assert_not_called()

    def test_init__single_mode(self, mock_group_init, mock_person_init):
        mock_data = generate_data_mock(group_mode=False)
        simulation = Simulation(mock_data)

        self.assertFalse(simulation.group_mode)
        mock_person_init.assert_called_once()
        mock_group_init.assert_not_called()

    @patch('finsim.simulation.Simulation._step_forward')
    def test_simulate__single_loop(self, mock_step, *_):
        mock_data = generate_data_mock()
        simulation = Simulation(mock_data)
        mock_step.return_value = True
        simulation.simulate()

        mock_step.assert_called_once()
        self.assertEqual(simulation.month, 1)

    @patch('finsim.simulation.Simulation._step_forward')
    def test_simulate__n_loop(self, mock_step, *_):
        mock_data = generate_data_mock()
        simulation = Simulation(mock_data)
        mock_step.side_effect = ([ False ] * 9) + [ True ]
        simulation.simulate()

        self.assertEqual(mock_step.call_count, 10)
        self.assertEqual(simulation.month, 10)

    @patch('finsim.simulation.Simulation._achieved_goal')
    def test_step_forward__standard_month(self, mock_goal, mock_group_init, _):
        mock_group = Mock()
        mock_group.updated = False
        mock_group_init.return_value = mock_group
        mock_goal.return_value = False
        mock_data = generate_data_mock()
        simulation = Simulation(mock_data)
        simulation.month = 4

        result = simulation._step_forward()

        mock_group.simulate_month.assert_called_once()
        mock_goal.assert_called_once()
        mock_group.begin_year.assert_not_called()
        mock_group.end_year.assert_not_called()
        mock_group.strategise.assert_not_called()
        self.assertFalse(result)

    @patch('finsim.simulation.Simulation._achieved_goal')
    def test_step_forward__first_month_of_year(self, mock_goal, mock_group_init, _):
        mock_group = Mock()
        mock_group.updated = False
        mock_group_init.return_value = mock_group
        mock_goal.return_value = False
        mock_data = generate_data_mock()
        simulation = Simulation(mock_data)
        simulation.month = 1

        result = simulation._step_forward()

        mock_group.simulate_month.assert_called_once()
        mock_goal.assert_called_once()
        mock_group.begin_year.assert_called_once()
        mock_group.end_year.assert_not_called()
        mock_group.strategise.assert_not_called()
        self.assertFalse(result)

    @patch('finsim.simulation.Simulation._achieved_goal')
    def test_step_forward__last_month_of_year(self, mock_goal, mock_group_init, _):
        mock_group = Mock()
        mock_group.updated = False
        mock_group_init.return_value = mock_group
        mock_goal.return_value = False
        mock_data = generate_data_mock()
        simulation = Simulation(mock_data)
        simulation.month = 12

        result = simulation._step_forward()

        mock_group.simulate_month.assert_called_once()
        mock_goal.assert_called_once()
        mock_group.begin_year.assert_not_called()
        mock_group.end_year.assert_called_once()
        mock_group.strategise.assert_not_called()
        self.assertFalse(result)

    @patch('finsim.simulation.Simulation._achieved_goal')
    def test_step_forward__updated(self, mock_goal, mock_group_init, _):
        mock_group = Mock()
        mock_group.updated = True
        mock_group_init.return_value = mock_group
        mock_goal.return_value = False
        mock_data = generate_data_mock()
        simulation = Simulation(mock_data)
        simulation.month = 5

        result = simulation._step_forward()

        mock_group.simulate_month.assert_called_once()
        mock_goal.assert_called_once()
        mock_group.begin_year.assert_not_called()
        mock_group.end_year.assert_not_called()
        mock_group.strategise.assert_called_once()
        self.assertFalse(result)

    @patch('finsim.simulation.Simulation._achieved_goal')
    def test_step_forward__updated_during_last_month(self, mock_goal, mock_group_init, _):
        mock_group = Mock()
        mock_group.updated = True
        mock_group_init.return_value = mock_group
        mock_goal.return_value = False
        mock_data = generate_data_mock()
        simulation = Simulation(mock_data)
        simulation.month = 12

        result = simulation._step_forward()

        mock_group.simulate_month.assert_called_once()
        mock_goal.assert_called_once()
        mock_group.begin_year.assert_not_called()
        mock_group.end_year.assert_called_once()
        mock_group.strategise.assert_not_called()
        self.assertFalse(result)

    @patch('finsim.simulation.Simulation._achieved_goal')
    def test_step_forward__goal_achieved(self, mock_goal, mock_group_init, _):
        mock_group = Mock()
        mock_group.updated = False
        mock_group_init.return_value = mock_group
        mock_goal.return_value = True
        mock_data = generate_data_mock()
        simulation = Simulation(mock_data)
        simulation.month = 6

        result = simulation._step_forward()

        mock_group.simulate_month.assert_called_once()
        mock_goal.assert_called_once()
        mock_group.begin_year.assert_not_called()
        mock_group.end_year.assert_not_called()
        mock_group.strategise.assert_not_called()
        self.assertTrue(result)

    @patch('finsim.simulation.Simulation._achieved_goal')
    def test_step_forward__updated_and_goal_achieved_in_last_month(self, mock_goal, mock_group_init, _):
        mock_group = Mock()
        mock_group.updated = True
        mock_group_init.return_value = mock_group
        mock_goal.return_value = True
        mock_data = generate_data_mock()
        simulation = Simulation(mock_data)
        simulation.month = 12

        result = simulation._step_forward()

        mock_group.simulate_month.assert_called_once()
        mock_goal.assert_called_once()
        mock_group.begin_year.assert_not_called()
        mock_group.end_year.assert_not_called()
        mock_group.strategise.assert_not_called()
        self.assertTrue(result)

    def test_achieved_goal__true(self, mock_group_init, _):
        mock_group = Mock()
        mock_group.total_saved.return_value = Decimal('25000')
        mock_group_init.return_value = mock_group
        mock_data = generate_data_mock()
        simulation = Simulation(mock_data)
        simulation.savings_goal = Decimal('24000')
        
        result = simulation._achieved_goal()
        self.assertTrue(result)

    def test_achieved_goal__perfect(self, mock_group_init, _):
        mock_group = Mock()
        mock_group.total_saved.return_value = Decimal('25000')
        mock_group_init.return_value = mock_group
        mock_data = generate_data_mock()
        simulation = Simulation(mock_data)
        simulation.savings_goal = Decimal('25000')
        
        result = simulation._achieved_goal()
        self.assertTrue(result)

    def test_achieved_goal__false(self, mock_group_init, _):
        mock_group = Mock()
        mock_group.total_saved.return_value = Decimal('24000')
        mock_group_init.return_value = mock_group
        mock_data = generate_data_mock()
        simulation = Simulation(mock_data)
        simulation.savings_goal = Decimal('25000')
        
        result = simulation._achieved_goal()
        self.assertFalse(result)









    """ def test_simulate__first_month(self, mock_group_init, _)
        mock_group = Mock()
        mock_group.total_saved.return_value = Decimal('1000')
        mock_group_init.return_value = mock_group

        mock_data = generate_data_mock()
        simulation = Simulation(mock_data)
        simulation.savings_goal = Decimal('1000')
        simulation.simulate()

        mock_group. """
