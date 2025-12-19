from odoo.tests.common import TransactionCase
from odoo.tools.misc import format_date

class TestAttendanceActivity(TransactionCase):
        
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        user_admin = self.env.ref("base.user_admin")
        self.env = self.env(user=user_admin)    
        self.activity = self.env["attendance.activity"].create({
            "name": "exampleName",
            "status_count": 0,    
        })
        print("--------------------SETUP DONE---------------------------")
   
    def test_fields_values_attendance_activity(self):
        self.assertEqual(self.activity.name,"exampleName")
        self.assertEqual(self.activity.status_count,0)
        print("----------TEST FIELDS VALUES ATTENDANCE ACTIVITY DONE--------------")
    
    def test__compute_status_count(self):
        result = self.activity._compute_status_count()
        self.assertEqual(result,None)
        print("----------TEST COMPUTE STATUS COUNT--------------------------------")
