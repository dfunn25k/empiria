import logging

from odoo.tests import tagged
from odoo.fields import Date
from dateutil.relativedelta import relativedelta
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


@tagged('-at_install', 'post_install')
class TestHrSalary(TransactionCase):
    
    def setUp(self):
        super().setUp()
        partner = self.env['res.partner'].create({
            'name': 'John Doe',
            'street': '123 Main St',
            'city': 'Metropolis',
            'country_id': self.env.ref('base.pe').id 
        })
        self.richard_emp = self.env['hr.employee'].create({
            'name': 'Richard',
            'gender': 'male',
            'birthday': '1984-05-01',
            'department_id': self.ref('hr.dep_rd'),
            'address_home_id':partner.id
        })
        
    def create_advance_salary(self):
        
        contract = self.env['hr.contract'].create({
            'date_end': Date.today() + relativedelta(years=2),
            'date_start': Date.to_date('2018-01-01'),
            'name': 'Contract for Richard',
            'wage': 5000.33,
            'employee_id': self.richard_emp.id,
            'struct_id': self.env['hr.payroll.structure'].search([], limit=1).id 
        })
        return self.env['hr.salary.advance'].create({
            'advance': 1.0,
            'employee_id': self.richard_emp.id,
            'employee_contract_id': contract.id,
        })
    
    def test_compute_sheet(self):
        specific_structure = self.env.ref('hr_loan_advance_other.hr_payroll_structure_loans')

        payslip_run = self.env['hr.payslip.run'].create({
            'date_end': '2024-07-01',
            'date_start': '2022-09-01',
            'name': 'Payslip for Employee'
        })

        payslip_employee = self.env['hr.payslip.employees'].create({
            'employee_ids': [(4, self.richard_emp.id)],
            'structure_id': specific_structure.id,
        })

        payslip_employee.with_context(active_id=payslip_run.id).compute_sheet()
        _logger.info('Test compute sheet')