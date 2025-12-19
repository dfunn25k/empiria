from odoo import api, fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Clientes',
        related='product_tmpl_id.partner_ids',
        help='Clientes a los que se les venderá este producto.',
        readonly=False
    )
    