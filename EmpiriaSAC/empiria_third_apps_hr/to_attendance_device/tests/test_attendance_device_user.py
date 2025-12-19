from odoo.tests.common import TransactionCase
from odoo.tools.misc import format_date

class TestAttendanceState(TransactionCase):
        
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        user_admin = self.env.ref("base.user_admin")
        self.env = self.env(user=user_admin)
        self.location = self.env["attendance.device.location"].create({
            "name":"locationExample"
        })
        self.employee = self.env["hr.employee"].create({
            "name":"employeeExample"
        })
        self.activity_is = self.env["attendance.activity"].create({
            "name": "exampleActivity"
        }) 
        self.state = self.env["attendance.state"].create({
            "name":"stateExample",
            "activity_id":self.activity_is.id,
            "code":14711,
            "type":"checkin",
        })
        self.device = self.env["attendance.device"].create({
            "name": "exampleDevice",
            "location_id":self.location.id,
            "firmware_version":"Examplefirmware_version",
            "serialnumber":"Exampleserialnumber",
            "oem_vendor":"Exampleoem_vendor",
            "platform":"Exampleplatform",
            "fingerprint_algorithm":"Examplefingerprint_algorithm",
            "device_name":"Example",
            "port":3000,
            "timeout":10,
        })            
        
    def test_fields_values_attedance_device_user(self):
        self.assertEqual(self.device.name, "exampleDevice")
        self.assertEqual(self.device.location_id.id,self.location.id )   
        self.assertEqual(self.device.firmware_version, "Examplefirmware_version")   
        self.assertEqual(self.device.serialnumber, "Exampleserialnumber")   
        self.assertEqual(self.device.oem_vendor, "Exampleoem_vendor")   
        self.assertEqual(self.device.platform, "Exampleplatform")   
        self.assertEqual(self.device.fingerprint_algorithm, "Examplefingerprint_algorithm")   
        self.assertEqual(self.device.device_name, "Example")   
        self.assertEqual(self.device.port, 3000)   
        self.assertEqual(self.device.timeout, 10)   
   
        print("-------------TEST FIELDS VALUES ATTENDANCE DEVICE USER DONE--------------")
        