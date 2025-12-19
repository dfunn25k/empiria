import logging

from odoo.exceptions import UserError
from odoo.tools import float_is_zero

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    delivery_order = fields.Boolean(
        string='Is Home Delivery Order'
    )

    def write(self, vals):
        for order in self:
            if order.name == '/' and order.delivery_order:
                vals['name'] = order.config_id.sequence_id._next()
        return super(PosOrder, self).write(vals)

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res['delivery_order'] = ui_order.get('delivery') or False
        return res

    @api.model
    def create_from_ui(self, orders, draft=False):
        pos_order_ids = super(PosOrder, self).create_from_ui(orders, draft=False)
        for order in pos_order_ids:
            order_rec = self.browse(order.get('id'))
            ref_order = [o['data'] for o in orders if o['data'].get('name') == order_rec.pos_reference]
            delivery_ids = self.env['pos.delivery.order'].sudo().search([('order_no', '=', order_rec.pos_reference)])
            if delivery_ids:
                delivery_ids.write({'pos_order_id': order.get('id')})
                # order_rec.write({'state': 'done'})
        return pos_order_ids

    # here I had a different flow, review in case the analyst requests that change !!!!

    def _process_payment_lines(self, pos_order, order, pos_session, draft):
        """Create account.bank.statement.lines from the dictionary given to the parent function.
        If the payment_line is an updated version of an existing one, the existing payment_line will first be
        removed before making a new one.
        :param pos_order: dictionary representing the order.
        :type pos_order: dict.
        :param order: Order object the payment lines should belong to.
        :type order: pos.order
        :param pos_session: PoS session the order was created in.
        :type pos_session: pos.session
        :param draft: Indicate that the pos_order is not validated yet.
        :type draft: bool.
        """
        prec_acc = order.pricelist_id.currency_id.decimal_places

        order_bank_statement_lines = self.env['pos.payment'].search([('pos_order_id', '=', order.id)])
        order_bank_statement_lines.unlink()
        if not order.delivery_order:
            for payments in pos_order['statement_ids']:
                order.add_payment(self._payment_fields(order, payments[2]))

        order.amount_paid = sum(order.payment_ids.mapped('amount'))

        if not draft and not float_is_zero(pos_order['amount_return'], prec_acc):
            cash_payment_method = pos_session.payment_method_ids.filtered('is_cash_count')[:1]
            if not cash_payment_method:
                raise UserError(_("No cash statement found for this session. Unable to record returned cash."))
            return_payment_vals = {
                'name': _('return'),
                'pos_order_id': order.id,
                'amount': -pos_order['amount_return'],
                'payment_date': fields.Date.context_today(self),
                'payment_method_id': cash_payment_method.id,
                'is_change': True,
            }
            order.add_payment(return_payment_vals)
