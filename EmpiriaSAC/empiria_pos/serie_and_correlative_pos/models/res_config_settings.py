from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_invoice_l10n_latam_document_type_ids = fields.Many2many(
        related='pos_config_id.invoice_l10n_latam_document_type_ids',
        readonly=False
    )
    pos_ticket_l10n_latam_document_type_ids = fields.Many2many(
        related='pos_config_id.ticket_l10n_latam_document_type_ids',
        readonly=False
    )
