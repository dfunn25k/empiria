from odoo.tests.common import TransactionCase

class TestHrPartnerConcept(TransactionCase):

    def setUp(self):
        super(TestHrPartnerConcept, self).setUp()
        
        self.structure_type = self.env['hr.payroll.structure.type'].create({
            'name': 'Tipo de Estructura de Prueba',
        })
        
        self.salary_structure = self.env['hr.payroll.structure'].create({
            'name': 'Estructura de prueba',
            'type_id': self.structure_type.id,
        })
        
        self.salary_rule_category = self.env['hr.salary.rule.category'].create({
            'name': 'Categoría de Prueba',
            'code': 'TEST',
        })
        
        self.salary_rule = self.env['hr.salary.rule'].create({
            'name': 'Regla de prueba',
            'code': 'TEST_RULE', 
            'sequence': 1,
            'quantity': 1,
            'struct_id': self.salary_structure.id,
            'category_id': self.salary_rule_category.id,
            'amount_select': 'fix',
            'amount_fix': 100.0,
        })
        
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
        })
        
        self.concept = self.env['hr.partner.concept'].create({
            'salary_rule': self.salary_rule.id,
            'partner_id': self.partner.id,
            'debit': True,
            'credit': False,
            'amount': 1000.0,
            'percentage': 10.0,
            'is_active': True,
            'start_date': '2024-09-01',
            'end_date': '2024-09-30',
        })
        
        self.employee = self.env['hr.employee'].create({
            'name': 'Empleado de Prueba',
        })

    def test_concept_creation(self):
        """Test para verificar la creación de conceptos salariales"""
        self.assertEqual(self.concept.salary_rule, self.salary_rule)
        self.assertEqual(self.concept.partner_id, self.partner)
        self.assertTrue(self.concept.debit)
        self.assertEqual(self.concept.amount, 1000.0)
        self.assertEqual(self.concept.percentage, 10.0)
    
    def test_employee_concept_assignment(self):
        """Test para asignar un concepto salarial a un empleado"""
        self.employee.write({'partner_concept_ids': [(4, self.concept.id)]})
        self.assertIn(self.concept, self.employee.partner_concept_ids)
        