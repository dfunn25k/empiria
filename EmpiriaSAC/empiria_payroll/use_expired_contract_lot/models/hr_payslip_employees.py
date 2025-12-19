# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from collections import defaultdict
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta
import pytz
from odoo.osv import expression
from odoo.tools import format_date

class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    employee_ids = fields.Many2many(
        'hr.employee', 'hr_employee_group_rel', 'payslip_id', 'employee_id', 'Employees',
        default=lambda self: self._get_employees(),
        required=True,
        context={'active_test': False},
        compute='_compute_employee_ids',
        store=True,
        readonly=False
    )

    def _get_available_contracts_domain(self):
        payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))
        domain = [('company_id', '=', self.env.company.id)]
        if payslip_run.use_expired_contract and payslip_run.date_start_contract and payslip_run.date_end_contract:
            try:
                query = f"""
                SELECT e.id
                FROM hr_employee e
                JOIN hr_contract c ON e.id = c.employee_id
                WHERE e.company_id = {self.env.company.id}
                AND c.state IN ('draft', 'open', 'close', 'cancel')
                AND (
                        (c.date_start BETWEEN '{payslip_run.date_start_contract}' AND '{payslip_run.date_end_contract}')
                        OR
                        (c.date_end BETWEEN '{payslip_run.date_start_contract}' AND '{payslip_run.date_end_contract}')
                    )
                AND e.active IN (True, False)
                AND c.active IN (True, False);
                """
                self.env.cr.execute(query)
                results = self.env.cr.dictfetchall()
                employee_ids = [result['id'] for result in results]
                domain = [('id', 'in', employee_ids)]
                print("Domain for employees: ", domain)
                employees = self.env['hr.employee'].sudo().with_context(active_test=False).search(domain)
                print("Found employees: ", employees)
                return domain
            except Exception as error:
                print("Error while executing query: ", error)
            return domain
        else:
            return [('contract_ids.state', 'in', ('open', 'close')), ('company_id', '=', self.env.company.id)]

    def _get_employees(self):
        payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))
        if payslip_run.use_expired_contract:
            domain = self._get_available_contracts_domain()
            employees = self.env['hr.employee'].sudo().with_context(active_test=False).search(domain)
            
            # Obtener contratos válidos para cada empleado
            valid_contracts = self.env['hr.contract'].sudo().search([
                ('employee_id', 'in', employees.ids),
                ('state', 'in', ['draft', 'open', 'close', 'cancel']),
                ('active', 'in', [True, False]),
                '|',
                    '&',
                    ('date_start', '<=', payslip_run.date_end_contract),
                    ('date_start', '>=', payslip_run.date_start_contract),
                    '&',
                    ('date_end', '>=', payslip_run.date_start_contract),
                    ('date_end', '<=', payslip_run.date_end_contract),
            ])

            # Agrupar contratos por empleado y seleccionar el más reciente
            employee_contracts = {}
            for contract in valid_contracts:
                employee_id = contract.employee_id.id
                if employee_id not in employee_contracts or contract.date_start > employee_contracts[employee_id].date_start:
                    employee_contracts[employee_id] = contract

            # Obtener los empleados con los contratos más recientes
            return self.env['hr.employee'].sudo().browse(employee_contracts.keys())
        else:
            return self.env['hr.employee'].sudo().search(self._get_available_contracts_domain())

    @api.depends('department_id')
    def _compute_employee_ids(self):
        for wizard in self:
            payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))
            domain = wizard._get_available_contracts_domain()
            if wizard.department_id:
                domain = expression.AND([
                    domain,
                    [('department_id', 'child_of', self.department_id.id)]
                ])
            if payslip_run.use_expired_contract:
                wizard.employee_ids = self.env['hr.employee'].with_context(active_test=False).search(domain)
            else:
                wizard.employee_ids = self.env['hr.employee'].search(domain)

    def compute_sheet(self):
        res = super(HrPayslipEmployees, self).compute_sheet()

        rule1 = self.env.ref('payroll_fields.hr_payslip_worked_days_company_rule')
        rule1.write({'domain_force': []})

        rule2 = self.env.ref('payroll_fields.hr_payslip_input_company_rule')
        rule2.write({'domain_force': []})

        if not self.env.context.get('active_id'):
            from_date = fields.Date.to_date(self.env.context.get('default_date_start'))
            end_date = fields.Date.to_date(self.env.context.get('default_date_end'))
            today = fields.date.today()
            first_day = today + relativedelta(day=1)
            last_day = today + relativedelta(day=31)
            if from_date == first_day and end_date == last_day:
                batch_name = from_date.strftime('%B %Y')
            else:
                batch_name = _('From %s to %s', format_date(self.env, from_date), format_date(self.env, end_date))
            payslip_run = self.env['hr.payslip.run'].create({
                'name': batch_name,
                'date_start': from_date,
                'date_end': end_date,
            })
        else:
            payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))

        employees = self.with_context(active_test=False).employee_ids if payslip_run.use_expired_contract else self.employee_ids
        # Prevent a payslip_run from having multiple payslips for the same employee
        employees -= payslip_run.slip_ids.employee_id
        payslips = self.env['hr.payslip']
        Payslip = self.env['hr.payslip']

        if payslip_run.use_expired_contract:
            contracts = self.env['hr.contract'].sudo().search([
                ('employee_id', 'in', employees.ids),
                ('state', 'in', ['draft', 'open', 'close', 'cancel']),
                ('active', 'in', [True, False]),
                '|',
                    '&',
                    ('date_start', '<=', payslip_run.date_end_contract),
                    ('date_start', '>=', payslip_run.date_start_contract),
                    '&',
                    ('date_end', '>=', payslip_run.date_start_contract),
                    ('date_end', '<=', payslip_run.date_end_contract),
            ])
            # Agrupar contratos por empleado y seleccionar el más reciente
            employee_contracts = {}
            for contract in contracts:
                employee_id = contract.employee_id.id
                if employee_id not in employee_contracts or contract.date_start > employee_contracts[employee_id].date_start:
                    employee_contracts[employee_id] = contract
            contracts = self.env['hr.contract'].sudo().browse([contract.id for contract in employee_contracts.values()])
        else:
            contracts = employees._get_contracts(
                payslip_run.date_start, payslip_run.date_end, states=['open', 'close']
            ).filtered(lambda c: c.active)

        default_values = Payslip.default_get(Payslip.fields_get())
        payslips_vals = []
        for contract in self._filter_contracts(contracts):
            values = dict(default_values, **{
                'name': _('New Payslip'),
                'employee_id': contract.employee_id.id,
                'payslip_run_id': payslip_run.id,
                'date_from': payslip_run.date_start,
                'date_to': payslip_run.date_end,
                'contract_id': contract.id,
                'struct_id': self.structure_id.id or contract.structure_type_id.default_struct_id.id,
            })
            payslips_vals.append(values)

        payslips = Payslip.with_context(tracking_disable=True).sudo().create(payslips_vals)
        payslips.sudo()._compute_name()
        payslips.sudo().compute_sheet()   
        payslip_run.state = 'verify'
        return res

    

