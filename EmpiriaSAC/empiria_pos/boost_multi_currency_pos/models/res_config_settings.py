from odoo import fields, models



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_enable_multi_currency = fields.Boolean(
        related='pos_config_id.enable_multi_currency',
        readonly=False
    )
    pos_display_conversion = fields.Boolean(
        related='pos_config_id.display_conversion',
        readonly=False
    )
    pos_fetch_master = fields.Boolean(
        related='pos_config_id.fetch_master',
        readonly=False
    )
    pos_currencies_ids = fields.Many2many(
        related='pos_config_id.currencies_ids',
        readonly=False
    )