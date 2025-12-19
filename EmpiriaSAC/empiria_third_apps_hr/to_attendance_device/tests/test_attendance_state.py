from odoo.tests.common import TransactionCase
from odoo.tools.misc import format_date

class TestAttendanceState(TransactionCase):
        
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        user_admin = self.env.ref("base.user_admin")
        self.env = self.env(user=user_admin)    
        self.activity = self.env["attendance.activity"].create({"name": "exampleActivity"})
        self.user = self.env["attendance.state"].create({
            "name": "exampleName",
            "activity_id":self.activity.id,
            "code":14711,
            "type":"checkin",    
        })
        print("--------------------SETUP DONE---------------------------")
        
       
 
    def test_fields_values_attendance_device_user(self):
        self.assertEqual(self.user.name,"exampleName")
        self.assertEqual(self.user.activity_id.id,self.user.activity_id.id)
        self.assertEqual(self.user.code,14711)
        self.assertEqual(self.user.type,"checkin")

        print("----------TEST FIELDS VALUES ATTENDANCE STATE DONE--------------")