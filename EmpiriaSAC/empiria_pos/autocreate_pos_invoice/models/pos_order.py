from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    l10n_latam_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal'
    )

    @api.model
    def _order_fields(self, ui_order):
        order = super(PosOrder, self)._order_fields(ui_order)
        if not ui_order.get('partner_id'):
            obj_session = self.env['pos.session'].browse(ui_order['pos_session_id'])
            order.update({'partner_id': obj_session.config_id.ticket_user_id.id})
        config_id = self.env['pos.session'].browse(ui_order['pos_session_id']).config_id
        order['l10n_latam_journal_id'] = config_id.invoice_journal_id.id if ui_order.get('to_invoice') else config_id.ticket_journal_id.id
        return order

    @api.model
    def _process_order(self, order, draft, existing_order):
        order_id = super(PosOrder, self)._process_order(order, draft, existing_order)
        obj_session = self.env['pos.session'].browse(order['data']['pos_session_id'])
        obj_config = obj_session.config_id
        state = self.browse(order_id).state
        if obj_config.always_move_account and state == 'paid' and self.browse(order_id).lines:
            self.browse(order_id).action_pos_order_invoice()
        return order_id

    def _prepare_invoice_vals(self):
        values = super(PosOrder, self)._prepare_invoice_vals()
        values['journal_id'] = self.l10n_latam_journal_id.id
        return values
