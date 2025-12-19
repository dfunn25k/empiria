from odoo import fields, models, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    invoice_l10n_latam_document_type_ids = fields.Many2many(
        comodel_name='l10n_latam.document.type',
        string='N° Invoice',
    )
    ticket_l10n_latam_document_type_ids = fields.Many2many(
        comodel_name='l10n_latam.document.type',
        relation='ticket_l10n_latam_document_type_ids_pos_config_rel',
        string='N° Ticket',
    )
