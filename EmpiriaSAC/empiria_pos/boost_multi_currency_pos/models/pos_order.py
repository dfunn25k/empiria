from odoo import models, fields, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    order_currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency list',
        readonly=True
    )
    amount_currency = fields.Float(string='Amount Currency')

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res.update({
            'order_currency_id': ui_order.get('order_currency_id') or False,
            'amount_currency': ui_order.get('amount_currency') or False
        })
        return res
