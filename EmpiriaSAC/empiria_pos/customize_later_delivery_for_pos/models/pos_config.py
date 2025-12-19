from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    flexible_ship_later = fields.Boolean(string='Flexibilizar política de control')
