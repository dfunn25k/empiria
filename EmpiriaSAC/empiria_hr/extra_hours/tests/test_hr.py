from odoo.tests.common import TransactionCase

class TestHr(TransactionCase):
        
    def setUp(self):
        super(TestHr, self).setUp()
        employees = self.env['hr.employee'].search([])
        for employee in employees:  
            existing_entry = self.env['hr.attendance'].search([('employee_id', '=', employee.id)])
            existing_entry.unlink()    
        
        self.ts_hr_attendance = self.env['hr.attendance'].create({
            'dayofweek': '0',
            'extra_hours': 0.0,
            'hours_part': 0.0,
            'difference':False,
            'employee_id':2
        })
        
        self.ts_res_config = self.env['res.config.settings'].create({
            'min_minutes_extra_hours':0.0,
            'diff_extra_part_min':0.0
        })
    
    def test_fields_val_res_config(self):
        self.assertEqual(self.ts_res_config.min_minutes_extra_hours, 0.0)
        self.assertEqual(self.ts_res_config.diff_extra_part_min, 0.0)
        print("---------------TEST FIELDS RES_CONFIG_SETTINGS OK----------")


                
    def test_fields_values(self):
        self.assertEqual(self.ts_hr_attendance.dayofweek, '0')
        self.assertEqual(self.ts_hr_attendance.extra_hours, 0.0)
        self.assertEqual(self.ts_hr_attendance.hours_part, 0.0)
        self.assertFalse(self.ts_hr_attendance.difference)
        print("---------------TEST FIELDS HR_ATTENDANCE OK----------")
    
    def test_functions_hr_attendance(self):
        self.assertEqual(self.ts_hr_attendance.get_period_odd_even_week(),'0')
        self.assertIsNone(self.ts_hr_attendance._compute_difference())
        self.assertIsNone(self.ts_hr_attendance._compute_dayofweek())
        self.assertIsNone(self.ts_hr_attendance.compute_hours_part())
        self.assertIsNone(self.ts_hr_attendance.action_get_extra_hours_lines())
        print("---------------TEST FUNCTIONS HR_ATTENDANCE OK----------")