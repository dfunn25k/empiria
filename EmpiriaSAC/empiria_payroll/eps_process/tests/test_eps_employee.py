from datetime import *

from odoo.tests import common

@common.tagged('post_install', '-at_install')
class TestEpsProcess(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner_id= self.env['res.partner'].create({
            'name': 'Prueba Seguro-Rimac',
        })
        self.partner_id_2= self.env['res.partner'].create({
            'name': 'Prueba Seguro-Positiva',
        })
        self.eps_credit = self.env['eps.credit'].create({
            'since': date(2024, 1, 1),
            'until': date(2024, 6, 30),
            'affiliated_workers': 1,
            'computable_remuneration_health_input':3.5,
            'eps_credit':50,
            'eps_service_cost':2.4,
            'uit':3.1,
            'uit_limit_affiliated_workers':1.5,
            'adjustment':1.2,
            'final_eps_credit':2.3
        })
        
        self.eps_management = self.env['eps.management'].create({
            'star_date': date(2024, 1, 1),
            'finish_date': date(2024, 6, 30),
            'entity':'Entidad',
            'partner_id': self.partner_id.id,
            'insurance': '43242323',
            'rate_employer':3.5,
            'amount_employer':2.5,
            'rate_worker':1.5,
            'amount_worker': 2.4,
            '_writing_employees':False,
        })
        
        self.employee = self.env['hr.employee'].create({
            'name': 'Empleado de Prueba',
            'exists_eps':True,
            'management_eps':self.eps_management.id,
        })
        
        
    def test_eps_credit_fields(self):
        self.assertEqual(self.eps_credit.since, date(2024, 1, 1))
        self.assertEqual(self.eps_credit.until, date(2024, 6, 30))
        self.assertEqual(self.eps_credit.affiliated_workers, 1)
        self.assertEqual(self.eps_credit.computable_remuneration_health_input, 3.5)
        self.assertEqual(self.eps_credit.eps_credit, 50)
        self.assertEqual(self.eps_credit.eps_service_cost, 2.4)
        self.assertEqual(self.eps_credit.uit, 3.1)
        self.assertEqual(self.eps_credit.uit_limit_affiliated_workers, 1.5)
        self.assertEqual(self.eps_credit.adjustment, 1.2)
        self.assertEqual(self.eps_credit.final_eps_credit, 2.3)    
    
    def test_eps_employee_flow(self):
        name_get = self.eps_management.name_get()   
        new_employee = self.env['hr.employee']
        
        employee_2 = new_employee.create({
            'name': 'Empleado de Prueba 2',
            'exists_eps':True,
            'management_eps':self.eps_management.id})
        
        employee_3 = new_employee.create({
            'name': 'Empleado de Prueba 3',
            'exists_eps':True,
            'management_eps':self.eps_management.id})
        
        employees = [employee.name for employee in employee_2.management_eps.employeer_ids]
        name, = name_get
        
        self.assertIn(employee_2.name,employees)
        self.assertIn(employee_3.name,employees)
        self.assertEqual(name[1],"{}-{}".format(self.eps_management.entity,self.eps_management.insurance))        
        self.assertEqual(self.eps_management.rate_employer,3.5)
        self.assertEqual(self.eps_management.amount_employer,2.5)
        self.assertEqual(self.eps_management.rate_worker,1.5)
        self.assertEqual(self.eps_management.amount_worker,2.4)
        print("----------TEST EPS PROCESS MANAGMENT EMPLOYEE OK----------")
    
    def test_validate_eps_process_by_employee(self):
        new_managment = self.env['eps.management']
                
        management_rimac = new_managment.create({
            'star_date': date(2024, 1, 1),
            'finish_date': date(2024, 8, 31),
            'entity':'Entidad-Rimac',
            'partner_id': self.partner_id.id,
            'insurance': '11111111',
            'rate_employer':3.5,
            'amount_employer':2.5,
            'rate_worker':1.5,
            'amount_worker': 2.4,
            'employeer_ids':[
                (0,0,{
                'name': 'Empleado Test',
                'exists_eps':True,
            })
                ],
            '_writing_employees':False,
        })
        
        management_postivia = new_managment.create({
            'star_date': date(2024, 6, 1),
            'finish_date': date(2024, 11, 30),
            'entity':'Entidad-Positiva',
            'partner_id': self.partner_id_2.id,
            'insurance': '22222222',
            'rate_employer':3.5,
            'amount_employer':2.5,
            'rate_worker':1.5,
            'amount_worker': 2.4,
            'employeer_ids':[
                (0,0,{
                'name': 'Empleado Test',
                'exists_eps':True,
            })
                ],
            '_writing_employees':False,
        })
        eps_managments = new_managment.search([('entity','in',['Entidad-Positiva','Entidad-Rimac'])])
        entitys_managments = [ ent.entity for ent in eps_managments]
        
        for insurance in eps_managments:
            for employee in insurance.employeer_ids:
                conflicting_insurances_up = eps_managments.search([
                    ('id', '!=', insurance.id),
                    ('employeer_ids', 'in', employee.id),
                    '|',
                    ('finish_date', '>=', insurance.finish_date),
                    ('finish_date', '>=', insurance.star_date)
                ])
                conflicting_insurances_down= eps_managments.search([
                    ('id', '!=', insurance.id),
                    ('employeer_ids', 'in', employee.id),
                    '|',
                    ('finish_date', '<=', insurance.finish_date),
                    ('finish_date', '<=', insurance.star_date)
                ])
                self.assertEqual(conflicting_insurances_up,conflicting_insurances_down)

        self.assertIn(management_rimac.entity,entitys_managments)
        self.assertIn(management_postivia.entity,entitys_managments)
        self.assertEqual(management_rimac.partner_id.id,self.partner_id.id)
        self.assertEqual(management_postivia.partner_id.id,self.partner_id_2.id)
        print("----------TEST EPS PROCESS BY EMPLOYEE OK----------")

