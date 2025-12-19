from odoo.tests import common
from odoo.tests.common import tagged
from datetime import *

@tagged('post_install', '-at_install')
class TestAutomaticTime(common.TransactionCase):
    def setUp(self):
        super().setUp()
        
        self.project = self.env['project.project'].create({
            'label_tasks':'Projecto 1 TEST',
            'name':'Test-Project'
        })
        
        self.employee = self.env['hr.employee'].create({
            'name':'employee test'
        })
        
        self.task = self.env['project.task'].create({
            'project_id':self.project.id,
            'name':'Task Test'
        })
        
        self.automatic = self.env['account.analytic.line'].create({
            'project_id':self.project.id,
            'employee_id':self.employee.id,
            'task_id':self.task.id,
            'date':date.today(),
            'fl_from':11.00,
            'fl_to':18.00,
        })
        
    def test_field_automatic(self):
        self.assertEqual(self.project.label_tasks, 'Projecto 1 TEST')
        self.assertEqual(self.project.name, 'Test-Project')
        self.assertEqual(self.employee.name, 'employee test')
        self.assertEqual(self.task.project_id.id, self.project.id)
        self.assertEqual(self.task.name, 'Task Test')
        self.assertEqual(self.automatic.project_id.id, self.project.id)
        self.assertEqual(self.automatic.employee_id.id, self.employee.id)
        self.assertEqual(self.automatic.task_id.id, self.task.id)
        
    def test_automatic_sheet(self):
        self.automatic.fl_from = 11.00
        self.automatic.fl_to = 18.00
       
        if self.automatic.fl_from < self.automatic.fl_to:
            self.automatic._onchange_unit_amount()
            self.assertEqual(self.automatic.unit_amount, 7.00)
            
        else:
            self.automatic._onchange_unit_amount()
            self.assertEqual(self.automatic.unit_amount, 0.00)