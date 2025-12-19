from odoo import fields, models, api


class PosOrder(models.Model):
    _inherit = "pos.order"

    account_move_rel_name = fields.Char(
        string='Invoice number',
        related='account_move.name',
        store=True
    )
    account_move_rel_document_type = fields.Char(
        string='Invoice document type',
        related='account_move.l10n_latam_document_type_id.name',
        store=True
    )
    account_move_rel_invoice_date = fields.Date(
        string='Invoice date',
        related='account_move.invoice_date',
        store=True
    )

    def _export_for_ui(self, order):
        order_list = super(PosOrder, self)._export_for_ui(order)
        order_list['account_move_rel_name'] = order.account_move_rel_name
        order_list['account_move_rel_document_type'] = order.account_move_rel_document_type
        order_list['account_move_rel_invoice_date'] = order.account_move_rel_invoice_date
        return order_list

    def _get_fields_for_draft_order(self):
        fields = super(PosOrder, self)._get_fields_for_draft_order()
        if fields is not None:
            fields.extend(['account_move_rel_name', 'account_move_rel_document_type', 'account_move_rel_invoice_date'])
        return fields
