from unittest import TestCase
from unittest.mock import patch, Mock
from decimal import Decimal

from finsim.sim_data import SimData, _lower_keys, DataImportError
from test_data import generate_test_data

@patch('finsim.sim_data.json_load')
class TestSimData(TestCase):

    @patch('finsim.sim_data._lower_keys', return_value={ 'test_data': 'test' })
    @patch('finsim.sim_data.SimData._process')
    def test_init(self, mock_process, mock_lower, mock_json):
        mock_json.return_value = generate_test_data()
        sim_data = SimData()

        mock_json.assert_called_once()
        mock_lower.assert_called_once()
        mock_process.assert_called_once()
        self.assertDictEqual(sim_data.data, { 'test_data': 'test' })

    def test_people(self, mock_json):
        mock_json.return_value = generate_test_data()
        sim_data = SimData()
        result = sim_data.get_people()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Alice')
        self.assertEqual(result[1]['name'], 'Bob')

    def test_get_shared_expenses(self, mock_json):
        mock_json.return_value = generate_test_data()
        sim_data = SimData()
        result = sim_data.get_shared_expenses()

        self.assertIn('monthly', result)
        self.assertIn('annual', result)
        self.assertEqual(len(result['monthly']), 2)
        self.assertEqual(len(result['annual']), 2)

    @patch('finsim.sim_data.SimData._validate_people')
    @patch('finsim.sim_data.SimData._validate_expenses')
    def test_process__group_mode(self, mock_val_exp, mock_val_people, mock_json):
        test_data = generate_test_data()
        mock_json.return_value = test_data
        sim_data = SimData()
        
        mock_val_people.assert_called_once()
        mock_val_exp.assert_any_call(test_data['group']['expenses'])
        self.assertEqual(sim_data.savings_goal, Decimal('10000'))


    @patch('finsim.sim_data.SimData._validate_people')
    @patch('finsim.sim_data.SimData._validate_expenses')
    def test_process__single_mode(self, mock_val_exp, mock_val_people, mock_json):
        test_data = generate_test_data()
        del test_data['group']
        del test_data['people'][1]
        mock_json.return_value = test_data
        sim_data = SimData()
        
        mock_val_people.assert_called_once()
        mock_val_exp.assert_not_called()
        self.assertEqual(sim_data.savings_goal, Decimal('10000'))

    @patch('finsim.sim_data.SimData._validate_people')
    @patch('finsim.sim_data.SimData._validate_expenses')
    def test_process__negative_savings_goal(self, mock_val_exp, mock_val_people, mock_json):
        test_data = generate_test_data()
        test_data['savings_goal'] = '-1000'
        mock_json.return_value = test_data
        
        with self.assertRaises(DataImportError) as context:
            sim_data = SimData()

        expected_err = 'Savings Goal must be greater than Zero.'
        self.assertEqual(expected_err, str(context.exception))

    @patch('finsim.sim_data.SimData._validate_people')
    @patch('finsim.sim_data.SimData._validate_expenses')
    def test_process__invalid_savings_goal(self, mock_val_exp, mock_val_people, mock_json):
        test_data = generate_test_data()
        test_data['savings_goal'] = 'LOTS OF MONEY'
        mock_json.return_value = test_data
        
        with self.assertRaises(DataImportError) as context:
            sim_data = SimData()

        expected_err = 'Savings Goal must be a valid number.'
        self.assertEqual(expected_err, str(context.exception))

    @patch('finsim.sim_data.SimData._validate_people')
    @patch('finsim.sim_data.SimData._validate_expenses')
    def test_process__missing_savings_goal(self, mock_val_exp, mock_val_people, mock_json):
        test_data = generate_test_data()
        del test_data['savings_goal']
        mock_json.return_value = test_data
        
        sim_data = SimData()

        self.assertIsNone(sim_data.savings_goal)
    

    def test_process_mode__ok_single(self, mock_json):
        test_data = generate_test_data()
        del test_data['group']
        del test_data['people'][1]
        mock_json.return_value = test_data
        sim_data = SimData()
        
        self.assertFalse(sim_data.group_mode)
        self.assertIsNone(sim_data.proportional_expenses)

    def test_process_mode__ok_group(self, mock_json):
        test_data = generate_test_data()
        mock_json.return_value = test_data
        sim_data = SimData()
        
        self.assertTrue(sim_data.group_mode)
        self.assertTrue(sim_data.proportional_expenses)

    def test_process_mode__err_no_people(self, mock_json):
        test_data = generate_test_data()
        test_data['people'] = []
        del test_data['group']
        mock_json.return_value = test_data

        with self.assertRaises(DataImportError) as context:
            sim_data = SimData()

        expected_err = 'The data file must contain at least one person.'
        self.assertEqual(expected_err, str(context.exception))

    def test_process_mode__err_redundant_group(self, mock_json):
        test_data = generate_test_data()
        del test_data['people'][1]
        mock_json.return_value = test_data

        with self.assertRaises(DataImportError) as context:
            sim_data = SimData()

        expected_err = '"Group" data is not permitted when only one person is defined.'
        self.assertEqual(expected_err, str(context.exception))

    def test_process_mode__err_missing_group(self, mock_json):
        test_data = generate_test_data()
        del test_data['group']
        mock_json.return_value = test_data

        with self.assertRaises(DataImportError) as context:
            sim_data = SimData()

        expected_err = 'If the data file contains more than one person, a "group" must be defined.'
        self.assertEqual(expected_err, str(context.exception))

    @patch('finsim.sim_data.SimData._validate_object')
    @patch('finsim.sim_data.SimData._validate_expenses')
    def test_validate_people__ok(self, mock_val_exp, mock_val_obj, _):
        test_data = generate_test_data()['people']
        SimData._validate_people(test_data)

        self.assertEqual(mock_val_obj.call_count, 7)
        self.assertEqual(mock_val_exp.call_count, 2)

    @patch('finsim.sim_data.SimData._validate_object')
    @patch('finsim.sim_data.SimData._validate_expenses')
    def test_validate_people__err_invalid_name(self, mock_val_exp, mock_val_obj, _):
        test_data = generate_test_data()['people']
        test_data[0]['name'] = 100

        with self.assertRaises(DataImportError) as context:
            SimData._validate_people(test_data)

        expected_err = 'Each person in the data file must have a valid name.'
        self.assertEqual(expected_err, str(context.exception))

    @patch('finsim.sim_data.SimData._validate_object')
    @patch('finsim.sim_data.SimData._validate_expenses')
    def test_validate_people__err_missing_savings(self, mock_val_exp, mock_val_obj, _):
        test_data = generate_test_data()['people']
        test_data[0]['savings'] = []

        with self.assertRaises(DataImportError) as context:
            SimData._validate_people(test_data)

        expected_err = 'Alice must have at least one savings account.'
        self.assertEqual(expected_err, str(context.exception))
    
    @patch('finsim.sim_data.SimData._validate_object')
    def test_validate_expenses__ok(self, mock_val_obj, _):
        test_data = generate_test_data()['people'][0]['expenses']
        SimData._validate_expenses(test_data)

        self.assertEqual(mock_val_obj.call_count, 2)
    
    @patch('finsim.sim_data.SimData._validate_object')
    def test_validate_expenses__err_negative_cost(self, mock_val_obj, _):
        test_data = generate_test_data()['people'][0]['expenses']
        test_data['monthly'][0]['cost'] = '-100'

        with self.assertRaises(DataImportError) as context:
            SimData._validate_expenses(test_data)

        expected_err = 'Expense costs must be greater than Zero.'
        self.assertEqual(expected_err, str(context.exception))
    
    @patch('finsim.sim_data.SimData._validate_object')
    def test_validate_expenses__err_invalid_cost(self, mock_val_obj, _):
        test_data = generate_test_data()['people'][0]['expenses']
        test_data['monthly'][0]['cost'] = 'ten'

        with self.assertRaises(DataImportError) as context:
            SimData._validate_expenses(test_data)

        expected_err = 'Expense costs must be a valid number.'
        self.assertEqual(expected_err, str(context.exception))
    
    @patch('finsim.sim_data.SimData._validate_object')
    def test_validate_expenses__err_invalid_inflation(self, mock_val_obj, _):
        test_data = generate_test_data()['people'][0]['expenses']
        test_data['monthly'][0]['inflation'] = 'yes'

        with self.assertRaises(DataImportError) as context:
            SimData._validate_expenses(test_data)

        expected_err = 'The "inflation" attribute of an expense item, if included, must be either "true" or "false".'
        self.assertEqual(expected_err, str(context.exception))
    
    def test_validate_object__ok(self, _):
        test_data = generate_test_data()['people'][0]
        SimData._validate_object(
            test_data,
            'person',
            req_attr=['name', 'salary', 'savings'],
            optional_attr=['expenses', 'debts']
        )
    
    def test_validate_object__err_missing_attr(self, _):
        test_data = generate_test_data()['people'][0]
        del test_data['salary']

        with self.assertRaises(DataImportError) as context:
            SimData._validate_object(
                test_data,
                'person',
                req_attr=['name', 'salary', 'savings'],
                optional_attr=['expenses', 'debts']
            )

        expected_err = '"person" object must contain a "salary" attribute.'
        self.assertEqual(expected_err, str(context.exception))
    
    def test_validate_object__err_invalid_attr(self, _):
        test_data = generate_test_data()['people'][0]
        test_data['invalid_attr'] = 'TEST'

        with self.assertRaises(DataImportError) as context:
            SimData._validate_object(
                test_data,
                'person',
                req_attr=['name', 'salary', 'savings'],
                optional_attr=['expenses', 'debts']
            )

        expected_err = '"invalid_attr" is not a valid attribute of "person".'
        self.assertEqual(expected_err, str(context.exception))

    def test_lower_keys(self, *_):
        test_data = generate_test_data()
        test_data['people'][0]['Name'] = test_data['people'][0]['name']
        test_data['group']['expenses']['monthly'][0]['Cost'] = test_data['group']['expenses']['monthly'][0]['cost']
        test_data['People'] = test_data['people']
        del test_data['group']['expenses']['monthly'][0]['cost']
        del test_data['people']

        result = _lower_keys(test_data)

        self.assertNotIn('People', result)
        self.assertIn('people', result)
        self.assertNotIn('Name', result['people'][0])
        self.assertIn('name', result['people'][0])
        self.assertNotIn('Cost', result['group']['expenses']['monthly'][0])
        self.assertIn('cost', result['group']['expenses']['monthly'][0])
        self.assertEqual(result['people'][0]['name'], 'Alice')
        self.assertEqual(result['group']['expenses']['monthly'][0]['cost'], '500.00')
