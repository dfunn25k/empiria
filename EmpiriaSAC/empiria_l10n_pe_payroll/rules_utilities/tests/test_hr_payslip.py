from odoo.tests.common import TransactionCase
from unittest.mock import patch, MagicMock
from datetime import date

class TestHrPayslip(TransactionCase):

    def setUp(self):
        super(TestHrPayslip, self).setUp()

        # Crear datos de prueba, como empleado, contrato y calendario
        self.employee = self.env['hr.employee'].create({
            'name': 'Test Employee',
        })

        self.contract = self.env['hr.contract'].create({
            'name': 'Test Contract',
            'employee_id': self.employee.id,
            'resource_calendar_id': self.env['resource.calendar'].create({
                'name': 'Test Calendar',
                'hours_per_day': 8.0,
            }).id,
            'wage': 1500.00,
        })

        self.payslip = self.env['hr.payslip'].create({
            'name': 'Test Payslip',
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'date_from': date(2023, 1, 1),
            'date_to': date(2023, 12, 31),
        })

        self.dias_010_entry_type = self.env['hr.work.entry.type'].create({
            'name': 'Días 010',
            'code': 'DIAS010',
            'sequence': 10,
            'utilities': True,
        })

        self.env['hr.payslip.worked_days'].create({
            'payslip_id': self.payslip.id,
            'employee_id': self.employee.id,
            'work_entry_type_id': self.dias_010_entry_type.id,
            'date_from': date(2022, 1, 1),  # Año anterior
            'date_to': date(2022, 12, 31),  # Año anterior
            'number_of_days': 20,
        })
        print("<<<<< SET UP >>>>>")


    def test_calculate_dias_010(self):

        self.employee = self.env['hr.employee'].create({
            'name': 'Test Employee',
        })
        worked_day_record = self.env['hr.payslip.worked_days'].create({
            'payslip_id': self.payslip.id,
            'employee_id': self.employee.id,
            'work_entry_type_id': self.dias_010_entry_type.id,
            'date_from': date(2022, 1, 1),
            'date_to': date(2022, 12, 31),
            'number_of_days': 20,
        })

        dias_010_days = self.payslip._calculate_dias_010()

        self.assertEqual(dias_010_days, 0)
        print("---TEST DIAS---")


    def test_get_worked_day_lines(self):
        with patch('odoo.addons.rules_utilities.models.hr_payslip.HrPayslip._calculate_dias_010', return_value=15):
            with patch.object(self.env, 'ref', return_value=self.dias_010_entry_type):
                work_day_lines = self.payslip._get_worked_day_lines()

                self.assertEqual(len(work_day_lines), 2)
                self.assertEqual(work_day_lines[0]['number_of_days'], 449.0)
                self.assertEqual(work_day_lines[0]['number_of_hours'], 3592.0)  # 449 días * 8 horas/día
                self.assertEqual(work_day_lines[0]['work_entry_type_id'], self.dias_010_entry_type.id)

        print("---TEST WORKED---")




