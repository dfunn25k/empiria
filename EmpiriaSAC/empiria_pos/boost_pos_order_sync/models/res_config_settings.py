from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_quotation_print_type = fields.Selection(
        related='pos_config_id.quotation_print_type',
        readonly=False
    )
    pos_send_orders_ids = fields.Many2many(
        related='pos_config_id.send_orders_ids',
        readonly=False
    )
