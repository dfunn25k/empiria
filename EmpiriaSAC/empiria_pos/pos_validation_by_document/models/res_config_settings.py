from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_identify_client = fields.Float(
        related='pos_config_id.identify_client', 
        readonly=False
    )
