from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    pos_allow_kitchens_receipt = fields.Boolean(
        related='pos_config_id.allow_kitchens_receipt',
        readonly=False
    )
    pos_use_multi_printer = fields.Boolean(
        related='pos_config_id.use_multi_printer',
        readonly=False
    )

    @api.onchange('pos_allow_kitchens_receipt')
    def _onchange_use_multi_printer(self):
        self.ensure_one()
        self.pos_use_multi_printer = False if not self.pos_allow_kitchens_receipt else self.pos_use_multi_printer
