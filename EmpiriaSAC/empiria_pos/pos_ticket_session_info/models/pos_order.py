from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    order_change = fields.Float(
        string='POS - Vuelto'
    )

    @api.model
    def _order_fields(self, ui_order):
        order = super(PosOrder, self)._order_fields(ui_order)
        order['order_change'] = ui_order.get('order_change', 0.00)
        return order

    def _prepare_invoice_vals(self):
        values = super(PosOrder, self)._prepare_invoice_vals()
        values['pos_order_change'] = self.order_change
        return values
