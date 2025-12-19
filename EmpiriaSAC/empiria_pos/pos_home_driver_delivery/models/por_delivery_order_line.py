from odoo import fields, models


class PosDeliveryOrderLine(models.Model):
    _name = "pos.delivery.order.line"
    _description = "POS Delivery Order Line"

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True
    )
    item_qty = fields.Float(
        string='Quantity'
    )
    item_rate = fields.Float(
        string='Price',
        digits=0
    )
    pos_delivery_id = fields.Many2one(
        comodel_name='pos.delivery.order',
        string='Delivery order'
    )
    item_note = fields.Char(
        string='Item Note',
        size=72
    )
