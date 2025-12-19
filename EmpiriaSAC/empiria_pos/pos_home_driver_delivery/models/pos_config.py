from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    verify_delivery = fields.Boolean(
        string='Home Delivery'
    )
