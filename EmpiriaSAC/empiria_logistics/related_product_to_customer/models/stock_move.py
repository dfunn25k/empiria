from odoo import api, fields, models

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            domain = [
                '|',
                ('product_tmpl_id.partner_ids', 'in', rec.picking_id.partner_id.id),
                ('product_tmpl_id.partner_ids', '=', False)]
            return {'domain': {'product_id': domain}}
            