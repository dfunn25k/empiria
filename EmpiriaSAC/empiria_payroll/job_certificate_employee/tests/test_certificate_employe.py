from odoo.tests import common
from unittest.mock import patch
from datetime import datetime
import pytz

class TestCertificateEmployee(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.employee = self.env['hr.employee'].create({
            'name': 'Juan Tito',
            'is_employer': True,
        })
        self.employee_user = self.env['res.users'].create({
            'name': 'Employee User',
            'login': 'employeeuser',
            'tz': 'America/Lima',
            'employee_id': self.employee.id,
        })
        print("<<<<< SET UP >>>>>>>")


    def test_search_employee(self):
        employee = self.employee.search_employee()
        self.assertEqual(employee.name, 'Juan Tito')
        self.assertTrue(employee.is_employer)
        print("<<<<< TEST 1 >>>>>>>")

    @patch('odoo.addons.hr.models.hr_employee.datetime')
    @patch('odoo.addons.hr.models.hr_employee.pytz')
    def test_date_today(self, mock_pytz, mock_datetime):
        mock_datetime.now.return_value = datetime(2024, 9, 10, 12, 0, 0)
        mock_pytz.timezone.return_value = pytz.timezone('America/Lima')

        self.employee._date_today()
        self.assertEqual(self.employee.date_today, '10 de setiembre de 2024')
        print("<<<<< TEST 2 >>>>>>>")

    def test_get_date_to_print(self):
        self.employee.date_today = '10 de septiembre de 2024'
        formatted_date = self.employee.get_date_to_print()
        self.assertEqual(formatted_date, '10 de septiembre del 2024')
        print("<<<<< TEST 3 >>>>>>>")


    @patch('odoo.api.Environment.ref')  
    def test_print_report(self, mock_ref):
        # Simular el comportamiento de report_action
        mock_report_action = mock_ref.return_value.report_action
        mock_report_action.return_value = 'mocked_report'

        result = self.env['hr.employee'].print_report()

        self.assertEqual(result, 'mocked_report')
        print("<<<<< TEST 4 >>>>>>>")


