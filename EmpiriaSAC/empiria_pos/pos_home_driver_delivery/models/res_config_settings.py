from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_verify_delivery = fields.Boolean(
        related='pos_config_id.verify_delivery',
        readonly=False
    )
