from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    identify_client = fields.Float(
        string='Identify customer from'
    )
