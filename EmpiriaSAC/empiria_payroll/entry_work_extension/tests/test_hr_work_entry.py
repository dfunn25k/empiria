from odoo.tests import common
from odoo.tests.common import tagged
from lxml import etree
from odoo import fields
import datetime

@tagged('post_install', '-at_install')
class TestHrWorkEntry(common.TransactionCase):
    
    def setUp(self):
        super().setUp()
        
        self.employee_1 = self.env['hr.employee'].create({
            'name': 'Employee 1',
        })
        self.employee_2 = self.env['hr.employee'].create({
            'name': 'Employee 2',
        })
        self.employee_3 = self.env['hr.employee'].create({
            'name': 'Employee 3',
        })
        
        self.wizard = self.env['hr.work.entry.regeneration.wizard'].create({
            'date_from': fields.Date.today(),
            'date_to': fields.Date.today() + datetime.timedelta(days=7),
            'employee_ids': [(6, 0, [self.employee_1.id])],
            'is_all_employees': False,
        })

    def test_compute_search_criteria_completed(self):
        self.wizard._compute_search_criteria_completed()
        self.assertFalse(self.wizard.search_criteria_completed)

        self.wizard.write({ 'is_all_employees':True })
        self.wizard._compute_search_criteria_completed()
        
        self.assertTrue(self.wizard.is_all_employees)

    def test_onchange_is_all_employees(self):
        view_id = self.env.ref('entry_work_extension.hr_work_entry_regeneration_wizard_inherit_entry_work_extension')
        view = self.env['ir.ui.view'].browse(view_id.id)
        
        xml_tree = etree.fromstring(view.arch)
        field = xml_tree.xpath("//field[@name='is_all_employees']")[0]
        field_name = field.get('name')
        self.assertTrue(field_name)       
        self.assertEqual(len(self.wizard.employee_ids), 1)
        self.assertEqual( view.model,'hr.work.entry.regeneration.wizard')

        self.wizard.write({ 'is_all_employees':True })
        self.wizard._onchange_is_all_employees()
        
        self.assertTrue(self.wizard.employee_ids)
        
        self.wizard.write({ 'is_all_employees':False })
        self.wizard._onchange_is_all_employees()

        self.assertFalse(self.wizard.employee_ids)