from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tariff_subheading_id = fields.Many2one(
        comodel_name='tariff.subheading',
        string='Sub-partida arancelaria SUNAT',
    )
