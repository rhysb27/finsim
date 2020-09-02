from decimal import InvalidOperation, Decimal as D
from sys import exit

from finsim.utils import round_currency_to_pounds
from finsim.debts import Debt

class UserRequestedRestart(Exception):
    pass

def initialise():
    print('\n\t============[ INITIALISING SIMULATION ]=============\n')

def begin():
    print('Done\n')
    print('\t====================================================')
    print('\t================[ START SIMULATION ]================')
    print('\t====================================================\n')
    print('You can use the following commands at any time:\n')
    print('\t\tRESTART STRATEGY: [R]\tQUIT: [Q]\n')

def display_annual_summary(model, year):
    print('\t=================[ END OF YEAR {} ]=================\n'.format(year))

def display_final_summary(model, total_months):
    years = total_months // 12
    months = total_months % 12
    print('\t====================================================')
    print('\t=================[ END SIMULATION ]=================')
    print('\t====================================================\n')
    print('Goal acheievd in {} years and {} months.\n'.format(years, months))

def cancel():
    print('\n\t====================================================')
    print('\t===============[ CANCEL SIMULATION ]================')
    print('\t====================================================\n')

def obtain_initial_strategy(person):
    print('\n\t----------------[ INITIAL STRATEGY ]----------------\n')
    name = person.name
    while True:
        try:
            print('Please provide an initial financial strategy for {}.'.format(name))
            strategy = _obtain_strategy(person)
            return strategy
        except UserRequestedRestart:
            print('\n\t--------------[ RESTARTING STRATEGY ]---------------\n')

def obtain_new_strategy(person):
    print('\n\t------------------[ NEW STRATEGY ]------------------\n')
    name = person.name
    cleared_list = person.debts.recently_cleared

    if len(cleared_list) == 0:
        cleared_hint = ''
    else:
        if len(cleared_list) == 1:
            cleared_string = cleared_list[0]
            for_hint = ' for {}'.format(name)
        else:
            and_cleared = [cleared_list.pop(), cleared_list.pop()]
            and_string = '{} and {}'.format(and_cleared[1], and_cleared[0])
            cleared_list.append(and_string)
            cleared_string = ', '.join(cleared_list)
        cleared_hint = '{} has paid off {}. '.format(name, cleared_string)
        for_hint = ''

    print('{}Please provide a new financial strategy{}.'.format(cleared_hint, for_hint))

    # TODO: Print current strategy.

    while True:
        try:
            strategy = _obtain_strategy(person)
            return strategy
        except UserRequestedRestart:
            print('\n\t--------------[ RESTARTING STRATEGY ]---------------\n')
            print('Please provide a new financial strategy for {}.'.format(name))

def _obtain_strategy(person):
    name = person.name
    disposable = round_currency_to_pounds(person.disposable_income)
    debts = person.debts.get_active()
    savings = person.savings_accounts.account_dict
    name_padding_len = max(len(k) for k in ([debt.name for debt in debts] + list(savings.keys())))
    amount_padding_len = len(str(disposable))

    line_1 = '{} has ~£{} disposable income per month and {} debts:\n'.format(name, disposable, len(debts))
    line_2 = '\nFirst, please input a monthly repayment amount for each debt:\n'
    line_3 = '\nNext, please input a monthly deposit for each savings account:\n'
    line_4 = '\nThank you. Here’s a summary of {}’s monthly strategy:\n'.format(name)
    line_5 = '\n    RESTART STRATEGY: [R]    QUIT: [Q]    CONFIRM: <any>\n'
    line_6 = '\n\t---------------[ ACCEPTED  STRATEGY ]---------------'

    strategy = {}
    
    print(line_1)
    _print_debt_summary(debts)
    print(line_2)
    strategy['debts'], rem_disposable = _obtain_account_payments(
        debts,
        disposable,
        name_padding_len,
        amount_padding_len)
    print(line_3)
    strategy['savings'], rem_disposable = _obtain_account_payments(
        savings,
        rem_disposable,
        name_padding_len,
        amount_padding_len)
    print(line_4)
    _print_strategy_summary(strategy)
    print(line_5)
    _handle_confirmation()
    print(line_6)
    return strategy


def _print_debt_summary(debts):
    # TODO: Refactor into Debts class?
    padding_length = max(len(debt.name) for debt in debts) + 3
    printout = ''
    for debt in debts:
        padded_name = '{}:'.format(debt.name).ljust(padding_length, ' ')
        printout += '\t{} £{}\n'.format(padded_name, debt.balance)

    print(printout)

def _print_strategy_summary(strategy):
    # TODO: Create strategy list object for final report.
    # TODO: Inform user of remaining income at Completion
    print('TODO')

def _obtain_account_payments(accounts, initial_disposable, name_padding_len, amount_padding_len):
    remaining_disposable = initial_disposable
    payments = {}
    prompt_template = '\t[£{} Remaining]    {} £'
    # TODO: Sort out accounts being dict and debts being list
    for name, account in accounts.items():
        padded_amount = str(remaining_disposable).ljust(amount_padding_len)
        padded_name = '{}:'.format(name).ljust(name_padding_len)
        prompt = prompt_template.format(padded_amount, padded_name)
        payment = _handle_user_input(prompt, name, remaining_disposable)
        payments[name] = payment
        remaining_disposable -= payment
    
    return payments, remaining_disposable

def _handle_user_input(prompt, name, remaining_disposable):
    acceptable = False
    while not acceptable:
        user_input = input(prompt)
        if user_input.upper() == 'Q':
            cancel()
            exit()
        elif user_input.upper() == 'R':
            raise UserRequestedRestart()

        try:
            repayment = D(user_input)
        except InvalidOperation:
            reprompt = '\n[ ERROR ]: Please input a valid number or keyboard command.\n'
            print(reprompt)
            continue

        if (remaining_disposable - repayment) <= D('0'):
            reprompt = '\n[ ERROR ]: Amount for {} exceeds remaining disposable income. Please enter a valid value.\n'.format(name)
            print(reprompt)
        else:
            acceptable = True

    return repayment

def _handle_confirmation():
    user_input = input('> ')
    if user_input.upper() == 'R':
        raise UserRequestedRestart()
    elif user_input.upper() == 'Q':
        cancel()
        exit()
    else:
        return

def _strike(text):
    result = ''
    for c in text:
        result = result + c + '\u0336'
    return result