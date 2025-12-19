from datetime import date
from odoo import models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_worked_day_lines(self, domain=None, check_out_of_contract=True):
        res = super(HrPayslip, self)._get_worked_day_lines(domain, check_out_of_contract)

        if self.contract_id.resource_calendar_id:
            hours_per_day = self.contract_id.resource_calendar_id.hours_per_day or 0.0
            # DIAS_010
            dias_010_days = self._calculate_dias_010()
            dias_010_hours = dias_010_days * hours_per_day
            dias_010_entry_type_id = self.env.ref('rules_utilities.hr_work_entry_type_dias_010')

            values = {
                'sequence': dias_010_entry_type_id.sequence,
                'work_entry_type_id': dias_010_entry_type_id.id,
                'number_of_days': dias_010_days,
                'number_of_hours': dias_010_hours,
            }
            res.append(values)

        return res

    def _calculate_dias_010(self):
        # Calcular el año anterior al de la fecha de fin del recibo de nómina
        previous_year = self.date_to.year - 1
        start_date = date(previous_year, 1, 1)
        end_date = date(previous_year, 12, 31)

        worked_days = self.env['hr.payslip.worked_days'].search([
            ('date_from', '>=', start_date),
            ('date_to', '<=', end_date),
            ('employee_id', '=', self.employee_id.id),
            ('work_entry_type_id.utilities', '=', True),
            ('payslip_id.struct_id.not_utilities_day_lines', '=', False)
        ])
        total_days = sum(worked_days.mapped('number_of_days'))

        return total_days
