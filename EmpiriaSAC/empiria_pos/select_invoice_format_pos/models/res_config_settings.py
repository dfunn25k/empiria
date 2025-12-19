from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_invoice_report_id = fields.Many2one(
        related='pos_config_id.invoice_report_id',
        readonly=False
    )
    pos_automatic_print_electronic_invoice = fields.Boolean(
        related='pos_config_id.automatic_print_electronic_invoice',
        readonly=False
    )

    @api.onchange('pos_iface_print_auto')
    def _onchange_pos_iface_print_auto(self):
        if self.pos_iface_print_auto:
            self.pos_automatic_print_electronic_invoice = False

    @api.onchange('pos_automatic_print_electronic_invoice')
    def _onchange_pos_automatic_print_electronic_invoice(self):
        if self.pos_automatic_print_electronic_invoice:
            self.pos_iface_print_auto = False
