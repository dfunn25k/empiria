from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from datetime import date

@tagged('-at_install', 'post_install')
class TestToleranceTardiness(TransactionCase):
    @classmethod
    def setUpClass(self):
        super(TestToleranceTardiness, self).setUpClass()
        self.employees = self.env['hr.employee'].search([])
        self.attendances = self.env['hr.attendance'].search([])
        self.company_temp = self.env['res.company'].create({
            'name': 'Company test',
        })
        self.attendance = self.env['hr.attendance'].create({
            'employee_id': self.employees[-1].id,
            'check_in': '2023-11-30 12:03:00',
            'check_out': '2023-11-30 21:00:00',
            'dayofweek': '3',
            'extra_hours': 0.0,
            'hours_part': 0.0,
            'difference':False
        })

    def test_tardiness(self):
        self.assertEqual(self.attendance.tardiness, '4 hora(s) 3 minuto(s)')
        self.attendance.write({'check_in':'2023-11-30 13:03:00'})
        self.assertEqual(self.attendance.tardiness, '5 hora(s) 3 minuto(s)')
        print("--------------------TEST TARDINESS OK---------------------")

    def test_fields_values(self):
        self.assertEqual(self.attendance.dayofweek, '3')
        self.assertEqual(self.attendance.extra_hours, 0.0)
        self.assertEqual(self.attendance.hours_part, 0.0)
        self.assertFalse(self.attendance.difference)
        print("---------------TEST HR_ATTENDANCE OK----------")

    def test_fun_hr_attendance(self):
        self.assertEqual(self.attendance.get_period_odd_even_week(),'1')
        self.assertRaises(self.attendance.convert_date_timezone(self.attendance.check_in))
        self.assertIsNotNone(self.attendance.convert_date_timezone(self.attendance.check_in))
        print("---------------TEST FUN HR_ATTENDANCE OK----------")