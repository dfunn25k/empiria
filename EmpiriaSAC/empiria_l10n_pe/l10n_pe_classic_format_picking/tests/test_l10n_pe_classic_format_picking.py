from odoo.tests import TransactionCase, tagged

@tagged('post_install', '-at_install')
class TestL10nPeClassicFormaPicking(TransactionCase):

    def setUp(self):
        super(TestL10nPeClassicFormaPicking, self).setUp()
        # Crear datos de prueba
        self.company = self.env['res.company'].create({
            'name': 'Test Company',
        })
        self.env.user.company_id = self.company
        
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'product',
            'weight': 10.0,
            'company_id': self.company.id,
        })
        
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'company_id': self.company.id,
        })
        
        self.warehouse = self.env['stock.warehouse'].create({
            'name': 'Test Warehouse',
            'code': 'TST',
            'partner_id': self.partner.id,
            'company_id': self.company.id,
        })
        
        self.location = self.env['stock.location'].create({
            'name': 'Test Location',
            'usage': 'internal',
            'warehouse_id': self.warehouse.id,
            'company_id': self.company.id,
        })

    def test_get_aggregated_product_weights(self):
        """ Probar que el peso del producto se agrega correctamente en el diccionario de resultados. """
        move_line = self.env['stock.move.line'].create({
            'product_id': self.product.id,
            'product_uom_id': self.product.uom_id.id,
            'qty_done': 1.0,
            'location_id': self.location.id,
            'location_dest_id': self.location.id,
            'company_id': self.company.id,
        })
        result = move_line._get_aggregated_product_weights()

        # Verificar que el peso del producto está presente y correcto
        first_key = next(iter(result))
        self.assertIn('weight', result[first_key])
        self.assertEqual(result[first_key]['weight'], 10.0)
        print('----------------------------TEST PRODUCT WEIGHT OK----------------------------')

    def test_default_direction_id(self):
        """ Probar que direction_id es False cuando la localización está inactiva o sin warehouse_id."""
        # Desactivar la localización
        self.location.active = False

        self.location._default_direction_id()
        self.assertFalse(self.location.direction_id)
        print('----------------------------TEST DIRECTION OK----------------------------')