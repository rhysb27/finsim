from json import load as json_load
from enum import Enum
from os import environ
from dotenv import load_dotenv
from decimal import InvalidOperation, Decimal as D

from finsim.utils import decimalise


load_dotenv('.env')
INFLATION_RATE = D(environ['INFLATION_RATE'])
NI_THRESHOLD = D(environ['NI_THRESHOLD'])
NI_RATE = D(environ['NI_RATE'])
IT_THRESHOLD = D(environ['IT_THRESHOLD'])
IT_RATE = D(environ['IT_RATE'])
SL_THRESHOLD = D(environ['SL_THRESHOLD'])
SL_RATE = D(environ['SL_RATE'])


class DataImportError(Exception):
    pass

class SimData:

    def __init__(self):
        with open('data.json', 'r') as f:
            raw_data = json_load(f)

        self.data = _lower_keys(raw_data)
        self._process()

    def get_people(self):
        return self.data['people']

    def get_shared_expenses(self):
        return self.data['group'].get('expenses', [])


    # -- Private Methods ----------------------------------
    
    def _process(self):
        self._process_mode()
        self._validate_people(self.data['people'])
        goal = self.data.get('savings_goal', None)
        if goal is not None:
            try:
                self.savings_goal = decimalise(goal)
                if self.savings_goal <= 0:
                    error_msg = 'Savings Goal must be greater than Zero.'
                    raise DataImportError(error_msg)
            except InvalidOperation:
                error_msg = 'Savings Goal must be a valid number.'
                raise DataImportError(error_msg)
        else:
            self.savings_goal = None
        if self.group_mode == True:
            group_expenses = self.data['group']['expenses']
            self._validate_expenses(group_expenses)

    def _process_mode(self):
        people = self.data.get('people', [])
        num_people = len(people)

        if num_people == 0 :
            error_msg = 'The data file must contain at least one person.'
            raise DataImportError(error_msg)
        elif num_people == 1:
            if 'group' in self.data:
                error_msg = '"Group" data is not permitted when only one person is defined.'
                raise DataImportError(error_msg)
            self.group_mode = False
            self.proportional_expenses = None
        else:
            if 'group' not in self.data:
                error_msg = 'If the data file contains more than one person, a "group" must be defined.'
                raise DataImportError(error_msg)
            self.group_mode = True
            self.proportional_expenses = self.data['group'].get('proportional_expenses', False)

    @staticmethod
    def _validate_people(people):
        for person in people:
            SimData._validate_object(
                person,
                'person',
                req_attr=['name', 'salary', 'savings'],
                optional_attr=['expenses', 'debts']
            )
            
            # Validate Person Names
            if not isinstance(person['name'], str):
                error_msg = 'Each person in the data file must have a valid name.'
                raise DataImportError(error_msg)
            
            # Validate Salaries
            salary = person['salary']
            SimData._validate_object(
                salary,
                'salary',
                req_attr=['base_salary'],
                optional_attr=['pension', 'payrise_rate']
            )

            # Validate Savings Accounts
            accounts = person['savings']
            if len(accounts) == 0:
                error_tmpl = '{} must have at least one savings account.'
                error_msg = error_tmpl.format(person['name'])
                raise DataImportError(error_msg)
            for account in accounts:
                SimData._validate_object(
                    account,
                    'savings',
                    req_attr=['name'],
                    optional_attr=['interest_rate', 'starting_balance', 'type']
                )
            
            # Validate Expenses
            SimData._validate_expenses(person['expenses'])

    @staticmethod
    def _validate_expenses(expenses):
        SimData._validate_object(
            expenses,
            'expenses',
            req_attr=[],
            optional_attr=['monthly', 'annual']
        )

        all_expenses = expenses.get('monthly', []) + expenses.get('annual', [])
        for item in all_expenses:
            SimData._validate_object(
                item,
                'expense',
                req_attr=['name', 'cost'],
                optional_attr=['inflation']
            )
            try:
                cost = decimalise(item['cost'])
                if cost <= 0:
                    error_msg = 'Expense costs must be greater than Zero.'
                    raise DataImportError(error_msg)
            except InvalidOperation:
                error_msg = 'Expense costs must be a valid number.'
                raise DataImportError(error_msg)

            if not isinstance(item.get('inflation', True), bool):
                error_msg = 'The "inflation" attribute of an expense item, if included, must be either "true" or "false".'
                raise DataImportError(error_msg)

    @staticmethod
    def _validate_object(obj, obj_name, req_attr, optional_attr):
        for attr in req_attr:
            if attr not in obj:
                error_msg = '"{}" object must contain a "{}" attribute.'.format(obj_name, attr)
                raise DataImportError(error_msg)
        for key in obj.keys():
            if key not in (req_attr + optional_attr):
                error_msg = '"{}" is not a valid attribute of "{}".'.format(key, obj_name)
                raise DataImportError(error_msg)

def _lower_keys(x):
    if isinstance(x, list):
        return [_lower_keys(v) for v in x]
    elif isinstance(x, dict):
        return dict((k.lower(), _lower_keys(v)) for k, v in x.items())
    else:
        return x
