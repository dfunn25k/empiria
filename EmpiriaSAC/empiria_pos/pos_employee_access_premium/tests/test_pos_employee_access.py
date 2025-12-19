from odoo.tests.common import TransactionCase

class TestPosEmployeeAccessPremium(TransactionCase):

    def setUp(self):
        super(TestPosEmployeeAccessPremium, self).setUp()
        self.employee = self.env['hr.employee'].create({
            'name': 'Test Employee',
            'pos_access_close': False,
            'pos_access_delete_order': True,
            'pos_access_delete_orderline': True,
            'pos_access_decrease_quantity': False,
            'pos_access_discount': True,
            'pos_access_payment': False,
            'pos_access_price': True,
        })
        self.pos_session = self.env['pos.session'].create({
            'config_id': self.env.ref('point_of_sale.pos_config_main').id
        })

        print("<<<<<< SET UP >>>>>>")

    def test_employee_access_rights(self):
        """Test employee's POS access rights"""
        # Verificar que el empleado no puede cerrar el POS
        self.assertFalse(self.employee.pos_access_close, "El empleado no deberia tener acceso para cerrar el POS")
        
        # Verificar que el empleado puede eliminar órdenes
        self.assertTrue(self.employee.pos_access_delete_order, "El empleado deberia tener acceso a eliminar ordenes")
        
        # Verificar que el empleado puede eliminar líneas de orden
        self.assertTrue(self.employee.pos_access_delete_orderline, "El empleado deberia tener acceso a eliminar order lines")
        
        # Verificar que el empleado no puede disminuir la cantidad de las líneas de orden
        self.assertFalse(self.employee.pos_access_decrease_quantity, "El empleado no deberia tener acceso a disminuir la cantidad")
        
        # Verificar que el empleado puede aplicar descuentos
        self.assertTrue(self.employee.pos_access_discount, "El empleado deberia tener acceso a aplicar descuentos")
        
        # Verificar que el empleado no puede procesar pagos
        self.assertFalse(self.employee.pos_access_payment, "El empleado no deberia tener acceso a procesar pagos")
        
        # Verificar que el empleado puede cambiar el precio
        self.assertTrue(self.employee.pos_access_price, "El empleado deberia tener acceso a cambiar el precio")

        print("<<<<<< TEST >>>>>>")
