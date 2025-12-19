from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from datetime import datetime

@tagged('post_install', '-at_install')
class TestUseExpiredContractLot(TransactionCase):

    def setUp(self):
        super(TestUseExpiredContractLot, self).setUp()
        self.Employee = self.env['hr.employee']
        self.Contract = self.env['hr.contract']
        self.PayslipRun = self.env['hr.payslip.run']
        self.Payslip = self.env['hr.payslip']
        self.PayslipEmployees = self.env['hr.payslip.employees']
        self.PayslipWorkedDays = self.env['hr.payslip.worked_days']
        self.HrWorkEntryType = self.env['hr.work.entry.type']
        self.PayrollStructure = self.env['hr.payroll.structure']
        self.PayrollStructureType = self.env['hr.payroll.structure.type']
        self.HrPayslipInput = self.env['hr.payslip.input']
    
    def test_generate_payslips_select_latest_contract(self):

        self.employee_1 = self.env['hr.employee'].create({'name': 'Employee 1'})
        self.employee_2 = self.env['hr.employee'].create({'name': 'Employee 2'})
        self.contract_1 = self.env['hr.contract'].create({
            'name': 'Contract 1',
            'employee_id': self.employee_1.id,
            'date_start': '2024-01-01',
            'date_end': '2024-06-01',
            'state': 'open',
            'wage': 10000,
        })
        self.contract_2 = self.env['hr.contract'].create({
            'name': 'Contract 2',
            'employee_id': self.employee_1.id,
            'date_start': '2024-06-02',
            'state': 'open',
            'wage': 10000,
        })
        self.contract_3 = self.env['hr.contract'].create({
            'name': 'Contract 3',
            'employee_id': self.employee_2.id,
            'date_start': '2024-02-01',
            'state': 'open',
            'wage': 10000,
        })

        payslip_run = self.env['hr.payslip.run'].create({
            'name': 'Test Payslip Run',
            'date_start': '2024-07-01',
            'date_end': '2024-07-31',
            'use_expired_contract': True,
            'date_start_contract': '2024-01-01',
            'date_end_contract': '2024-07-31',
        })

        payslip_employees = self.env['hr.payslip.employees'].create({
            'employee_ids': [(6, 0, [self.employee_1.id, self.employee_2.id])],
        })

        # Llamar al método compute_sheet para generar las nóminas
        payslip_employees.with_context(active_id=payslip_run.id).compute_sheet()

        # Obtener los contratos seleccionados
        selected_contracts = self.env['hr.payslip'].search([('payslip_run_id', '=', payslip_run.id)]).mapped('contract_id')

        # Verificar que no haya empleados duplicados
        employee_ids = selected_contracts.mapped('employee_id.id')
        self.assertEqual(len(employee_ids), len(set(employee_ids)), "Hay empleados duplicados en los contratos seleccionados")

        # Verificar que el contrato más reciente es el seleccionado
        self.assertIn(self.contract_2, selected_contracts, "El contrato más reciente no fue seleccionado para Employee 1")
        self.assertIn(self.contract_3, selected_contracts, "El contrato más reciente no fue seleccionado para Employee 2")
        print('------------TEST OK VERIFICACION DE EMPLEADOS DUPLICADOS------------')

    def test_payroll_with_expired_contracts(self):
        year = datetime.now().year

        # Create the Payroll Structure Type
        payroll_structure_type = self.PayrollStructureType.create({
            'name': 'Worker Structure Test Type',
            'wage_type': 'monthly',
        })
        
        # Create the Payroll Structure
        payroll_structure = self.PayrollStructure.create({
            'name': 'Worker Structure Test',
            'type_id': payroll_structure_type.id,
            'input_line_type_ids': [
                (0, 0, {
                    'name': 'Bonus',
                    'code': 'BONUS',
                }),
                (0, 0, {
                    'name': 'Commission',
                    'code': 'COMM',
                }),
            ],
        })

        # Crear empleado A y su contrato
        employee_a = self.Employee.create({
            'name': 'Empleado A',
            'identification_id': 'A001',
        })
        contract_a = self.Contract.create({
            'name': 'Contrato A',
            'employee_id': employee_a.id,
            'date_start': f'{year - 1}-01-01',
            'date_end': f'{year - 1}-10-31',
            'wage': 10000,
            'structure_type_id': payroll_structure.type_id.id,
        })

        # Crear empleado B y su primer contrato (B1)
        employee_b = self.Employee.create({
            'name': 'Empleado B',
            'identification_id': 'B001',
        })
        contract_b1 = self.Contract.create({
            'name': 'Contrato B1',
            'employee_id': employee_b.id,
            'date_start': f'{year - 2}-01-01',
            'date_end': f'{year - 1}-03-31',
            'wage': 10000,
            'structure_type_id': payroll_structure.type_id.id,
            'state': 'close',  # Estado “Vencido”
        })

        # Crear el segundo contrato de empleado B (B2)
        contract_b2 = self.Contract.create({
            'name': 'Contrato B2',
            'employee_id': employee_b.id,
            'date_start': f'{year - 1}-04-01',
            'date_end': False,
            'wage': 10000,
            'structure_type_id': payroll_structure.type_id.id,
            'state': 'open',  # Estado: “En Progreso”
        })

        # Crear empleado C y su contrato
        employee_c = self.Employee.create({
            'name': 'Empleado C',
            'identification_id': 'C001',
            'active': False,
        })
        contract_c = self.Contract.create({
            'name': 'Contrato C',
            'employee_id': employee_c.id,
            'date_start': f'{year - 1}-01-01',
            'date_end': False,
            'wage': 10000,
            'structure_type_id': payroll_structure.type_id.id,
            'state': 'open',  # Estado: “En Progreso”
        })

        # Crear lote de nómina con contratos expirados
        payslip_run = self.PayslipRun.create({
            'name': 'Lote de nómina - marzo',
            'use_expired_contract': True,
            'date_start': f'{year}-03-01',
            'date_end': f'{year}-03-31',
            'date_start_contract': f'{year - 1}-01-01',
            'date_end_contract': f'{year - 1}-12-31',
        })

        # Generar recibos de nómina usando el asistente hr.payslip.employees
        payslip_employees_wizard = self.PayslipEmployees.with_context(active_id=payslip_run.id).create({
            'employee_ids': [(6, 0, [employee_a.id, employee_b.id, employee_c.id])]
        })
        payslip_employees_wizard.compute_sheet()

        # Verificar si los recibos de nómina están generados
        payslips = self.Payslip.search([('payslip_run_id', '=', payslip_run.id)])

        self.assertEqual(len(payslips), len(payslip_employees_wizard.employee_ids), "La cantidad de recibos de nómina generados deben ser iguales")

        # Depuración: imprimir recibos de nómina generados y añadir días trabajados
        for count, payslip in enumerate(payslips, start=1):
            # Crear tipo de entrada de trabajo
            work_entry_type = self.HrWorkEntryType.create({
                'name': f'Extra attendance {count}',
                'is_leave': False,
                'code': f'WORKTEST{count}',
            })

            # Crear líneas de días trabajados para el recibo de nómina
            self.PayslipWorkedDays.create({
                'payslip_id': payslip.id,
                'sequence': count,
                'work_entry_type_id': work_entry_type.id,
            })

            # for input in payslip.input_line_ids:
            self.HrPayslipInput.create({
                'payslip_id': payslip.id,
                'input_type_id': self.env.ref('hr_payroll.input_deduction').id,
                'name': 'Test Input Type',
                'amount': 0,
                'struct_id':payroll_structure.id,
            })

            print(f"Recibo de nómina generado para empleado {payslip.employee_id.name}, contrato: {payslip.contract_id.name}")
        
        payslip_a = payslips.filtered(lambda p: p.employee_id == employee_a)
        payslip_b = payslips.filtered(lambda p: p.employee_id == employee_b)

        self.assertTrue(payslip_a, "Debe existir un recibo de nómina para el empleado A")
        self.assertTrue(payslip_b, "Debe existir un recibo de nómina para el empleado B")

        self.assertEqual(payslip_a.contract_id.id, contract_a.id, "Payslip de empleado A debe usar contrato A")
        self.assertEqual(payslip_b.contract_id.id, contract_b2.id, "Payslip de empleado B debe usar contrato B2")
        self.assertTrue(payslip_run.use_expired_contract, "El lote de nómina debe incluir contratos expirados")

        # Verificar si los recibos de nómina tienen días trabajados y entradas
        for payslip in payslips:
            payslip.compute_sheet()
            self.assertGreater(len(payslip.worked_days_line_ids), 0, f"El recibo de nómina para {payslip.employee_id.name} debe tener días trabajados")
            self.assertTrue(payslip.input_line_ids, "Las líneas de entrada de recibo de nomina deben ser generadas")
        
        print('------------TEST OK------------')






