from odoo.tests import common
from odoo.tests.common import tagged
from datetime import *
from odoo import fields
from dateutil.relativedelta import relativedelta

HOURS_PER_DAY = 8
@tagged('post_install', '-at_install')
class TestCompensatedHrs(common.TransactionCase):
    def setUp(self):
        super().setUp()
        
        self.project = self.env['project.project'].create({
            'label_tasks':'Projecto Compensate TEST',
            'name':'Test-Project'
        })
        
        self.employee = self.env['hr.employee'].create({
            'name':'employee'
        })
        
        self.task = self.env['project.task'].create({
            'project_id':self.project.id,
            'name':'Task Compensate'
        })
        
        self.analytic_line = self.env['account.analytic.line'].create({
            'project_id':self.project.id,
            'employee_id':self.employee.id,
            'task_id':self.task.id,
            'date':date.today(),
            'fl_from':14.00,
            'fl_to':19.00,
            'is_validate_extra_hour':True
        })
        
        self.holiday_status = self.env.ref('automatic_leave_type.hr_leave_type_27')
        
    
    def test_compensated_lines(self):
        self.assertEqual(self.project.label_tasks, 'Projecto Compensate TEST')
        self.assertEqual(self.project.name, 'Test-Project')
        self.assertEqual(self.employee.name, 'employee')
        self.assertEqual(self.task.project_id.id, self.project.id)
        self.assertEqual(self.task.name, 'Task Compensate')
        self.assertEqual(self.analytic_line.project_id.id, self.project.id)
        self.assertEqual(self.analytic_line.employee_id.id, self.employee.id)
        self.assertEqual(self.analytic_line.task_id.id, self.task.id)
        
    
    def test_action_validate_extra_hours(self):
        """Test the action_validate_extra_hours method."""

        self.analytic_line.action_validate_extra_hours()
        self.assertTrue(self.analytic_line.is_validate_extra_hour, "Extra hours should be marked as validated.")

     
        date_review = fields.Date.today() - relativedelta(days=1)
        allocation = self.env['hr.leave.allocation'].search([
            ('employee_id', '=', self.employee.id),
            ('from_date', '=', date_review),
            ('to_date', '=', date_review),
            ('holiday_type', '=', 'employee'),
            ('holiday_status_id', '=', self.holiday_status.id),
        ],limit=1)
        if not allocation:
            self.assertFalse(allocation)
        else:
            self.assertTrue(allocation, "Leave allocation created.")

            expected_days = self.analytic_line.hours_compensate / HOURS_PER_DAY
            self.assertAlmostEqual(allocation.number_of_days, expected_days)
