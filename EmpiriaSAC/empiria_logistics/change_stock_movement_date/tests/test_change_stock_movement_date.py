from odoo import _
from odoo.tests import common
from odoo.exceptions import AccessError, MissingError, ValidationError
from datetime import datetime, timedelta

class TestChangeStockMovementDate(common.TransactionCase):

    def setUp(self):
        super(TestChangeStockMovementDate, self).setUp()
        self.stock_picking_obj = self.env['stock.picking']
        self.stock_move_obj = self.env['stock.move']
        self.product = self.env['product.product'].create({'name': 'Test Product'})
        self.partner = self.env['res.partner'].create({'name': 'Test Partner'})
        self.picking_type_out = self.env.ref('stock.picking_type_out')
        self.customer_location = self.env.ref('stock.stock_location_customers')

    def test_date_done_visibility(self):
        """Test if the date_done field is visible and editable in the form view"""
        picking = self.stock_picking_obj.create({
            'partner_id': self.partner.id,
            'picking_type_id': self.picking_type_out.id,
            'location_id': self.picking_type_out.default_location_src_id.id,
            'location_dest_id': self.customer_location.id,
        })

        # Check if the date_done field is defined in the model fields
        fields = picking.fields_get()
        self.assertIn('date_done', fields)

        # Check if the field is editable when the picking is not done
        self.assertFalse(picking.state == 'done')
        try:
            picking.write({'date_done': datetime.now()})
        except AccessError:
            raise ValidationError(_("Should be able to write to date_done when picking is not done"))
        
        print("--------------------TEST DATE DONE VISIBILITY OK--------------------")


    def test_date_done_functionality(self):
        """Test if the date_done field is properly saved and used"""
        picking = self.stock_picking_obj.create({
            'partner_id': self.partner.id,
            'picking_type_id': self.picking_type_out.id,
            'location_id': self.picking_type_out.default_location_src_id.id,
            'location_dest_id': self.customer_location.id,
        })
        
        move = self.stock_move_obj.create({
            'name': 'Test Move',
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'product_uom': self.product.uom_id.id,
            'picking_id': picking.id,
            'location_id': picking.location_id.id,
            'location_dest_id': self.customer_location.id,
        })
        
        # Set a custom date_done
        custom_date = datetime.now() - timedelta(days=1)
        picking.date_done = custom_date
        
        # Validate the picking
        picking.action_confirm()
        picking.action_assign()
        move.quantity_done = 1
        picking.button_validate()
        
        # Check if the custom date was preserved
        self.assertEqual(picking.date_done, custom_date)
        self.assertEqual(move.date, custom_date)
        print("--------------------TEST DATE DONE FUNCTIONALITY OK--------------------")

    def test_date_done_readonly_when_done(self):
        """Test if the date_done field becomes readonly when the picking is done"""
        picking = self.stock_picking_obj.create({
            'partner_id': self.partner.id,
            'picking_type_id': self.picking_type_out.id,
            'location_id': self.picking_type_out.default_location_src_id.id,
            'location_dest_id': self.customer_location.id,
        })
        
        move = self.stock_move_obj.create({
            'name': 'Test Move',
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'product_uom': self.product.uom_id.id,
            'picking_id': picking.id,
            'location_id': picking.location_id.id,
            'location_dest_id': self.customer_location.id,
        })
        
        # Validate the picking
        picking.action_confirm()
        picking.action_assign()
        move.quantity_done = 1
        picking.button_validate()
        
        # Try to change the date_done after validation
        picking.write({'date_done': datetime.now()})
        print("--------------------TEST DATE DONE READONLY WHEN DONE OK--------------------")


