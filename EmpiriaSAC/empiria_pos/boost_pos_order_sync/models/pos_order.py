from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    quote_id = fields.Many2one(
        comodel_name='pos.quote',
        string='Related Quote',
        readonly=True
    )

    @api.model
    def _order_fields(self, ui_order):
        fields_return = super(PosOrder, self)._order_fields(ui_order)
        if ui_order.get('quote_id', False):
            fields_return.update({'quote_id': ui_order.get('quote_id', '')})
        return fields_return

    def write(self, vals):
        for order in self:
            if vals.get('state') and vals['state'] == 'paid' and order.name == '/':
                order.quote_id.write({'state': 'done'})
        return super(PosOrder, self).write(vals)
