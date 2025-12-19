from odoo import api, fields, models

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            domain = [
                '|',
                ('partner_ids', 'in', rec.picking_id.partner_id.id),
                ('partner_ids', '=', False)]
            return {'domain': {'product_id': domain}}
            