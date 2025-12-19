from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestHrLeaveAbsence(TransactionCase):
        
    def setUp(self):
        super(TestHrLeaveAbsence, self).setUp()
        
        self.employee = self.env['hr.employee'].search([])
        
        for record in self.employee:
            existing_attendance = self.env['hr.attendance'].search([('employee_id', '=', record.id)], limit=1)
            if not existing_attendance:
                self.holiday = self.env['hr.attendance'].create({
                    'employee_id': record.id
                })
                
        self.ts_hr_leave = self.env['hr.leave'].create({
            'employee_id':105,
            'holiday_status_id':16,
            'report_attendance': True,
            'state': 'draft',
            'private_name': 'Permiso personal',
            'active': True,
            'number_of_days': 1,
            'duration_display': '1 días',
            'date_from': '2023-11-17 00:00:00',  
            'date_to': '2023-11-17 23:59:59'
        })
        print("-------------SETUP OK-------------")
           
    def test_fields_hr_leave_absence(self):
        self.assertEqual(self.ts_hr_leave.employee_id.id, 105)
        self.assertEqual(self.ts_hr_leave.holiday_status_id.id, 16)
        self.assertTrue(self.ts_hr_leave.report_attendance)
        self.assertEqual(self.ts_hr_leave.state, 'draft')
        self.assertEqual(self.ts_hr_leave.private_name, 'Permiso personal')
        self.assertTrue(self.ts_hr_leave.active)
        self.assertEqual(self.ts_hr_leave.number_of_days, 1)
        self.assertEqual(self.ts_hr_leave.duration_display, '1 días')
        print("---------------TEST FIELDS OK------------------")
        
    def test_funtion_leave_absence(self):
        try:
            schedule = self.employee.resource_calendar_id
        except ValidationError:
            schedule = self.env['resource.calendar'].create({
                'name': 'Standard 35 hours/week',
            })
            self.employee.write({'resource_calendar_id': schedule.id})     
        self.assertEqual(self.ts_hr_leave.get_period_odd_even_week(), '0')
        self.assertIsNone(self.ts_hr_leave._action_absence_monitor())
        self.assertIsNone(self.employee._compute_last_attendance_id())
        print("---------------TEST FUNCTION OK------------------")
