from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    l10n_latam_document_type_id = fields.Many2one(
        comodel_name='l10n_latam.document.type',
        string='Document type',
    )

    @api.model
    def _order_fields(self, ui_order):
        values = super(PosOrder, self)._order_fields(ui_order)
        values.update({'l10n_latam_document_type_id': ui_order.get('l10n_latam_document_type_id', False)})
        return values

    def _prepare_invoice_vals(self):
        move_values = super(PosOrder, self)._prepare_invoice_vals()
        if self.l10n_latam_document_type_id:
            move_values.update({'l10n_latam_document_type_id': self.l10n_latam_document_type_id.id,})
        return move_values
