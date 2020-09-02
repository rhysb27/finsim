from decimal import ROUND_DOWN, ROUND_UP, Context, Decimal as D

def decimalise(value):
    return D(str(value))

def round_currency(value, round_up=False):
    """
    Rounds the amount to two decimal places using the current ``Decimal`` rounding algorithm.
    """
    round_direction = ROUND_UP if round_up else ROUND_DOWN
    return D(value.quantize(D('.01'), rounding=round_direction))

def round_currency_to_pounds(value, round_up=False):
    """
    Rounds the amount to zero decimal places using the current ``Decimal`` rounding algorithm.
    """
    round_direction = ROUND_UP if round_up else ROUND_DOWN
    return D(value.quantize(D('1'), rounding=round_direction))

def get_percentage_of(value, percentage, round_up=False):
    return round_currency( value * (percentage / D('100')), round_up ) 


