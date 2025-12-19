from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestRelatedProductCustomer(TransactionCase):

    def setUp(self):
        super(TestRelatedProductCustomer, self).setUp()
        self.product_obj = self.env['product.product']
        self.partner_obj = self.env['res.partner']
        self.stock_move_obj = self.env['stock.move']
        self.stock_move_line_obj = self.env['stock.move.line']
        self.picking_obj = self.env['stock.picking']

        self.partner1 = self.partner_obj.create({'name': 'Cliente 1'})
        self.partner2 = self.partner_obj.create({'name': 'Cliente 2'})
        
        self.product1 = self.product_obj.create({
            'name': 'Producto 1',
            'type': 'product',
            'partner_ids': [(6, 0, [self.partner1.id])]
        })
        self.product2 = self.product_obj.create({
            'name': 'Producto 2',
            'type': 'product',
        })

    def test_product_partner_relation(self):
        """Probar la relación entre productos y clientes"""
        self.assertIn(self.partner1, self.product1.partner_ids)
        self.assertNotIn(self.partner2, self.product1.partner_ids)
        self.assertEqual(len(self.product2.partner_ids), 0)

    def test_stock_move_domain(self):
        """Probar el dominio en stock.move"""
        picking = self.picking_obj.create({
            'partner_id': self.partner1.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
        })
        
        move = self.stock_move_obj.new({
            'name': 'Test Move',
            'picking_id': picking.id,
            'product_id': self.product1.id,
            'product_uom': self.product1.uom_id.id,
            'product_uom_qty': 1,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
        })
        
        result = move.onchange_product_id()
        domain = result.get('domain', {}).get('product_id', [])
        
        self.assertTrue(('product_tmpl_id.partner_ids', 'in', self.partner1.id) in domain)
        self.assertTrue(('product_tmpl_id.partner_ids', '=', False) in domain)

    def test_stock_move_line_domain(self):
        """Probar el dominio en stock.move.line"""
        picking = self.picking_obj.create({
            'partner_id': self.partner1.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
        })
        
        move_line = self.stock_move_line_obj.new({
            'picking_id': picking.id,
            'product_id': self.product1.id,
            'product_uom_id': self.product1.uom_id.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
        })
        
        result = move_line.onchange_product_id()
        domain = result.get('domain', {}).get('product_id', [])
        
        self.assertTrue(('partner_ids', 'in', self.partner1.id) in domain)
        self.assertTrue(('partner_ids', '=', False) in domain)
