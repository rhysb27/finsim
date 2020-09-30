from decimal import InvalidOperation, Decimal as D
from sys import exit

from finsim.utils import round_currency_to_pounds
from finsim.debts import Debt

class UserRequestedRestart(Exception):
    pass

class UI:

    # -- Basic Output Functions -------------------------------------

    @staticmethod
    def initialise():
        print(UI._heading('INITIALISING SIMULATION', level=2))

    @staticmethod
    def begin():
        print('Done')
        print(UI._heading('START SIMULATION', level=1))
        print('You can use the following commands at any time:\n')
        print('\t\tRESTART STRATEGY: [R]\tQUIT: [Q]\n')

    @staticmethod
    def cancel():
        print(UI._heading('CANCEL SIMULATION', level=1))

    @staticmethod
    def end_year(model, year):
        heading = UI._heading('END OF YEAR {}'.format(year), level=2)
        print('Total saved to date: £{}'.format(model.total_saved()))
        # TODO: Show annual report for each person

    @staticmethod
    def end(total_months):
        years = total_months // 12
        year_label = 'year' if years == 1 else 'years'
        months = total_months % 12
        month_label = 'month' if months == 1 else 'months'
        print(UI._heading('END SIMULATION', level=1))
        print('Goal achieved in {} {} and {} {}.\n'.format(
            years,
            year_label,
            months,
            month_label))
        # TODO: Reference final report save location.

    # -- Initialisation Functions -----------------------------------
    
    @staticmethod
    def obtain_savings_goal():
        print('Please provide a savings goal.\n')
        acceptable = False
        while not acceptable:
            user_input = input('\t£')
            if user_input.upper() == 'Q':
                UI.cancel()
                exit()

            try:
                goal = D(user_input)
            except InvalidOperation:
                print(UI._err('Please input a valid number or keyboard command.'))
                continue

            if goal <= D('0'):
                print(UI._err('Please enter a savings goal greater than 0.'))
            else:
                acceptable = True

        return goal


    # -- Strategy Functions -----------------------------------------

    def obtain_initial_strategy(self, person):
        self._prepare_data_for_strategy(person)
        print(UI._heading('INITIAL STRATEGY', level=3))
        while True:
            try:
                print('Please provide an initial financial strategy for {}.'.format(person.name))
                strategy = self._obtain_strategy()
                return strategy
            except UserRequestedRestart:
                self._prepare_data_for_strategy(person)
                print(UI._heading('RESTARTING STRATEGY', level=3))

    def obtain_new_strategy(self, person):
        self._prepare_data_for_strategy(person)
        print(UI._heading('NEW STRATEGY', level=3))
        print(self._new_strategy_hint())
        print('Here is their previous strategy:\n')
        print(self._summarise_strategy(person.current_strategy))

        while True:
            try:
                strategy = self._obtain_strategy()
                return strategy
            except UserRequestedRestart:
                self._prepare_data_for_strategy(person)
                print(UI._heading('RESTARTING STRATEGY', level=3))
                print('Please provide a new financial strategy for {}.'.format(person.name))


    # -- Strategy Helpers -------------------------------------------

    def _prepare_data_for_strategy(self, person):
        self.current_person = person
        self.recently_cleared = person.debts.recently_cleared
        self.remaining_disposable = round_currency_to_pounds(person.disposable_income)
        self.debts = person.debts.to_list()
        self.savings = person.savings.to_list()
        self.acc_padding = max( len(a.name) for a in (self.debts + self.savings) ) + 2
        self.rem_padding = len(str(self.remaining_disposable))

    def _new_strategy_hint(self):
        cleared = self.recently_cleared
        name = self.current_person.name
        if len(cleared) == 0:
            hint_template = 'Please provide a new strategy for {}.\n'
            return hint_template.format(name)

        if len(cleared) == 1:
            cleared_string = cleared[0]
        else:
            and_cleared = [ cleared.pop(), cleared.pop() ]
            and_string = '{} and {}'.format(and_cleared[1], and_cleared[0])
            cleared.append(and_string)
            cleared_string = ', '.join(cleared)

        hint_template = '{} has paid off {}. Please provide a new strategy for them.\n'
        return hint_template.format(name, cleared_string)

    def _summarise_strategy(self, strategy):
        summary = ''
        item_template = '{} £{}'
        line_template = '\t{}\n'

        for item in (strategy.get('debts', []) + strategy['savings']):
            padded_name = self._pad_name(item['name'])
            item_str = item_template.format(padded_name, item['payment'])
            if item['name'] in self.recently_cleared:
                item_line = line_template.format(UI._strike(item_str))
            else:
                item_line = line_template.format(item_str)
            summary += item_line
            

        padded_name = self._pad_name('Remaining')
        rem_line = item_template.format(padded_name, strategy['remaining'])
        summary += line_template.format('-' * len(rem_line))
        summary += line_template.format(rem_line)
        return summary

    def _obtain_strategy(self):    
        strategy = {}
        if len(self.debts) > 0:
            debt_str = 'debt' if len(self.debts) == 1 else 'debts'
            print('{} has ~£{} disposable income per month and {} {}:\n'.format(
                self.current_person.name, self.remaining_disposable, len(self.debts), debt_str))
            print(self.current_person.debts.to_string())

            print('\nFirst, please input a monthly repayment amount for each debt:\n')
            strategy['debts'] = self._obtain_account_payments(self.debts)

            print('\nNext, please input a monthly deposit for each savings account:\n')
        else:
            print('{} has ~£{} disposable income per month.\n'.format(
                self.current_person.name, self.remaining_disposable))

            print('\nPlease input a monthly deposit for each savings account:\n')
        strategy['savings'] = self._obtain_account_payments(self.savings)
        strategy['remaining'] = self.remaining_disposable

        print('\nThank you. Here’s a summary of {}’s monthly strategy:\n'.format(self.current_person.name))
        print(self._summarise_strategy(strategy))
        print('\n    RESTART STRATEGY: [R]    QUIT: [Q]    CONFIRM: <any>\n')
        self._handle_confirmation()

        print(UI._heading('ACCEPTED STRATEGY', level=3))
        return strategy

    def _obtain_account_payments(self, accounts):
        payments = []
        for account in accounts:
            padded_amount = str(self.remaining_disposable).ljust(self.rem_padding)
            padded_name = self._pad_name(account.name)
            prompt = '\t[£{} Remaining]    {} £'.format(padded_amount, padded_name)
            payment = self._handle_user_input(prompt)
            payments.append({ 'name': account.name, 'payment': payment })
            self.remaining_disposable -= payment

        return payments

    def _handle_user_input(self, prompt):
        acceptable = False
        while not acceptable:
            user_input = input(prompt)
            if user_input.upper() == 'Q':
                UI.cancel()
                exit()
            elif user_input.upper() == 'R':
                raise UserRequestedRestart()

            try:
                payment = D(user_input)
            except InvalidOperation:
                print(UI._err('Please input a valid number or keyboard command.'))
                continue

            if (self.remaining_disposable - payment) <= D('0'):
                print(UI._err('Payment amount exceeds remaining disposable income. Please enter a valid value.'))
            else:
                acceptable = True

        return payment

    def _handle_confirmation(self):
        user_input = input('> ')
        if user_input.upper() == 'R':
            raise UserRequestedRestart()
        elif user_input.upper() == 'Q':
            UI.cancel()
            exit()
        else:
            return


    # -- Formatters -------------------------------------------------

    @staticmethod
    def _heading(text, level):
        width = 52
        line_char = '=' if level <= 2 else '-'
        main_line = '[ {} ]'.format(text).center(width, line_char)
        if level == 1:
            emphasis_line = line_char * width
            heading = '\n\t{}\n\t{}\n\t{}\n'.format(emphasis_line, main_line, emphasis_line)
        else:
            heading = '\n\t{}\n'.format(main_line)
        return heading

    @staticmethod
    def _strike(text):
        result = ''
        for c in text:
            result = result + c + '\u0336'
        return result

    @staticmethod
    def _err(text):
        return '\n[ ERROR ]: {}\n'.format(text)

    def _pad_name(self, account_name):
        return '{}:'.format(account_name).ljust(self.acc_padding)