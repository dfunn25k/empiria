from odoo import models, fields


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    line_amount_currency = fields.Float(string='Amount Currency')
