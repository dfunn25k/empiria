from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_flexible_ship_later = fields.Boolean(related='pos_config_id.flexible_ship_later', readonly=False)
