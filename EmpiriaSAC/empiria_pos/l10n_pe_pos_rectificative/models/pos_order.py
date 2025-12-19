from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _prepare_invoice_vals(self):
        move_values = super(PosOrder, self)._prepare_invoice_vals()
        if self.l10n_latam_document_type_id.code in ['07', '08'] and self.company_id.country_id.code == 'PE':
            move_values.update({
                'l10n_pe_edi_cancel_reason': 'Devolución por ítem',
                'l10n_pe_edi_refund_reason': '07',
            })
        return move_values
