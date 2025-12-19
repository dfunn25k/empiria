from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    reference_rectified = fields.Char(string='Reference')
    date_rectified = fields.Datetime(string='Date rectified')
    invoice_reference_type_l10n_latam_document_type_ids = fields.Many2one(
        comodel_name='l10n_latam.document.type',
        string='Invoice reference documents types'
    )
    ticket_reference_type_l10n_latam_document_type_ids = fields.Many2one(
        comodel_name='l10n_latam.document.type',
        string='Ticket reference document types'
    )

    @api.model
    def _order_fields(self, ui_order):
        values = super(PosOrder, self)._order_fields(ui_order)
        values.update({
            'reference_rectified': ui_order.get('reference_rectified', False),
            'date_rectified': ui_order.get('date_rectified', False),
            'invoice_reference_type_l10n_latam_document_type_ids': ui_order.get('invoice_reference_type_l10n_latam_document_type_ids', False),
            'ticket_reference_type_l10n_latam_document_type_ids': ui_order.get('ticket_reference_type_l10n_latam_document_type_ids', False)
        })
        return values

    def _prepare_invoice_vals(self):
        move_values = super(PosOrder, self)._prepare_invoice_vals()
        if self.reference_rectified and self.date_rectified:
            move_values.update({
                'origin_number': self.reference_rectified,
                'origin_invoice_date': self.date_rectified,
                'origin_l10n_latam_document_type_id': self.ticket_reference_type_l10n_latam_document_type_ids.id if self.ticket_reference_type_l10n_latam_document_type_ids else self.invoice_reference_type_l10n_latam_document_type_ids.id,
            })
        return move_values
