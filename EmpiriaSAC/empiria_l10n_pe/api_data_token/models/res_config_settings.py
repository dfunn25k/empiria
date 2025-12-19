from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    api_data_token = fields.Char(
        string='API Token',
        config_parameter='api.access_token',
        default="RAcSGWD1TgC7VdjCTOZSVA=="
    )
