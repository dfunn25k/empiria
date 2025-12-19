from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Clientes',
        store=True,
        help='Clientes a los que se les venderá este producto.'
    )
    