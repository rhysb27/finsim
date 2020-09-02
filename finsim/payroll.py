from os import environ

from finsim.utils import round_currency, get_percentage_of, decimalise as D
import finsim.sim_data as data

class Payroll:
    def __init__(self, salary_data):
        self.gross = D(salary_data['base_salary'])
        self.pension_rate = D(salary_data.get('pension', 0))
        self.payrise_rate = D(salary_data.get('payrise_rate', data.INFLATION_RATE))
        self._calculate_net_salary()

    def payrise(self):
        payrise_amount = get_percentage_of(self.gross, self.payrise_rate)
        self.gross += payrise_amount
        self._calculate_net_salary()

    def _calculate_net_salary(self):
        pension_deduction = get_percentage_of(self.gross, self.pension_rate)
        gross_after_pension = self.gross - pension_deduction

        ni_deduction = get_percentage_of(
            (gross_after_pension - data.NI_THRESHOLD), data.NI_RATE )
        it_deduction = get_percentage_of(
            (gross_after_pension - data.IT_THRESHOLD), data.IT_RATE )
        sl_deduction = get_percentage_of(
            (gross_after_pension - data.SL_THRESHOLD), data.SL_RATE )

        net = gross_after_pension - (ni_deduction + it_deduction + sl_deduction)
        self.net_monthly = round_currency( net / 12 )
