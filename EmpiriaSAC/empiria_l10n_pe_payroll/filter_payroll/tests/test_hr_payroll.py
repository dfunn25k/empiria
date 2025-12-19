from odoo.tests.common import TransactionCase
from odoo.tests.common import tagged

@tagged('post_install', '-at_install')
class TestHrPayroll(TransactionCase):

    def setUp(self):
        super().setUp()
        self.WorkEntryType = self.env['hr.work.entry.type']
        self.LeaveType = self.env['hr.leave.type']
        self.PayslipWorkedDays = self.env['hr.payslip.worked_days']
        self.Leave = self.env['hr.leave']
        self.Attendance = self.env['hr.attendance']
        self.employee = self.env['hr.employee'].create({
            'name': 'Test Employee',
            'active': True,
        })

        self.contract = self.env['hr.contract'].create({
            'name':'Contrato/Empleado',
            'employee_id': self.employee.id,
            'state': 'open',
            'date_start': '2024-01-01',
            'date_end': '2024-12-31',
            'wage':1000,
            'wage_type':'monthly'
        })
        self.payslip = self.env['hr.payslip'].create({
            'name':self.employee.name,
            'employee_id': self.employee.id,
            'date_from': '2024-09-01',
            'date_to': '2024-09-30',
            'state': 'done'
        })
     
        self.work_entry_type = self.WorkEntryType.create({
            'name': 'Test Work Entry Type',
            'unpaid': True,
            'code':'C-100',
            'is_social_benefits_license': True,
            'is_benefits_license_absence': False,
            'is_calc_own_rule': True
        })

        self.leave_type = self.LeaveType.create({
            'name': 'Test Leave Type',
            'work_entry_type_id': self.work_entry_type.id,
        })

        self.payslip_worked_days = self.PayslipWorkedDays.create({
            'name': 'Test Payslip Worked Days',
            'work_entry_type_id': self.work_entry_type.id,
            'payslip_id' : self.payslip.id
        })


       

    def test_work_entry_type_fields(self):
        self.assertTrue(self.work_entry_type.unpaid)
        self.assertTrue(self.work_entry_type.is_social_benefits_license)
        self.assertFalse(self.work_entry_type.is_benefits_license_absence)
        self.assertTrue(self.work_entry_type.is_calc_own_rule)

    def test_leave_type_fields(self):
        self.assertEqual(self.leave_type.unpaid, self.work_entry_type.unpaid)
        self.assertEqual(self.leave_type.is_social_benefits_license, self.work_entry_type.is_social_benefits_license)
        self.assertEqual(self.leave_type.is_benefits_license_absence, self.work_entry_type.is_benefits_license_absence)
        self.assertEqual(self.leave_type.is_calc_own_rule, self.work_entry_type.is_calc_own_rule)

    def test_payslip_worked_days_fields(self):
        self.assertEqual(self.payslip_worked_days.unpaid, self.work_entry_type.unpaid)
        self.assertEqual(self.payslip_worked_days.is_social_benefits_license, self.work_entry_type.is_social_benefits_license)
        self.assertEqual(self.payslip_worked_days.is_benefits_license_absence, self.work_entry_type.is_benefits_license_absence)
        self.assertEqual(self.payslip_worked_days.is_calc_own_rule, self.work_entry_type.is_calc_own_rule)
