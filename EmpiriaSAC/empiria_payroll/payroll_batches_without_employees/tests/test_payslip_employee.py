from odoo.tests import common
from odoo.tests.common import tagged
from lxml import etree
from odoo import fields
import datetime

@tagged('post_install', '-at_install')
class TestPayslipEmployee(common.TransactionCase):
    
    def setUp(self):
        super().setUp()
        
        self.payslip_employees = self.env['hr.payslip.employees'].create({
            'structure_id': self.env['hr.payroll.structure'].search([], limit=1).id,
            'department_id': self.env['hr.department'].search([], limit=1).id,
        })
        
        self.employee = self.env['hr.employee'].create({
            'name': 'Test Employee',
        })

    def test_payslip_employee(self):
        self.payslip_employees.write({
            'employee_ids': [(6, 0, [self.employee.id])]
        })
        action = self.payslip_employees.clean_employees()
        view_id = self.env.ref('payroll_batches_without_employees.hr_payslip_employees_form_view_inherit_payroll_batches_without_employees')
        view = self.env['ir.ui.view'].browse(view_id.id)
        
        xml_tree = etree.fromstring(view.arch)
        field = xml_tree.xpath("//button[@name='clean_employees']")[0]
        field_name = field.get('name')
        
        self.assertEqual(field_name,'clean_employees')
        self.assertFalse(self.payslip_employees.employee_ids)

        self.assertEqual(action['name'], 'Generar recibos de nómina')
        self.assertEqual(action['res_model'], 'hr.payslip.employees')
        self.assertEqual(action['res_id'], self.payslip_employees.id)
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['target'], 'new')