from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError

class TestThirdPartiesDelivery(TransactionCase):

    def setUp(self):
        super(TestThirdPartiesDelivery, self).setUp()
        self.partner_1 = self.env['res.partner'].create({'name': 'Partner 1'})
        self.partner_2 = self.env['res.partner'].create({'name': 'Partner 2'})
        self.stock_picking = self.env['stock.picking']

    def test_create_stock_picking(self):
        picking = self.stock_picking.create({
            'partner_id': self.partner_1.id,
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
        })
        self.assertEqual(picking.customer_id, self.partner_1, "customer_id debe establecerse en partner_id en el momento de la creación")

    def test_onchange_deliver_to_third_parties(self):
        picking = self.stock_picking.new({
            'partner_id': self.partner_1.id,
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
        })
        picking.deliver_to_third_parties = True
        picking.onchange_deliver_to_third_parties()
        self.assertEqual(picking.customer_id, self.partner_1, "customer_id debe establecerse en partner_id cuando deliver_to_third_parties es verdadero")

    def test_onchange_partner_id(self):
        picking = self.stock_picking.new({
            'partner_id': self.partner_1.id,
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
        })
        picking.partner_id = self.partner_2
        picking.onchange_deliver_partner_id()
        self.assertEqual(picking.customer_id, self.partner_2, "customer_id debe actualizarse cuando partner_id cambia y deliver_to_third_parties es falso")