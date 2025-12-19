from odoo import models
from odoo.tools import float_is_zero


class PosPayment(models.Model):
    _inherit = "pos.payment"

    def _create_payment_moves(self, is_reverse=False):
        result = self.env['account.move']
        for payment in self:
            payment_method = payment.payment_method_id
            if payment_method.type == 'pay_later' or float_is_zero(payment.amount, precision_rounding=payment.pos_order_id.currency_id.rounding):
                continue
            payment_move = payment._create_payment_move_entry(is_reverse)
            payment.write({'account_move_id': payment_move.id})
            result |= payment_move
            payment_move._post()
        return result
