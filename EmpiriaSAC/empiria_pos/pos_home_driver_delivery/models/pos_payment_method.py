from odoo.exceptions import UserError

from odoo import api, fields, models, _


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    is_home_delivery = fields.Boolean(
        string='Use as Home Delivery',
        related='journal_id.is_home_delivery',
        readonly=False
    )

    @api.model
    def create(self, vals):
        methods = self.search_count([('is_home_delivery', '=', True)])
        if 'is_home_delivery' in vals:
            if vals.get('is_home_delivery') == True:
                if methods >= 1:
                    raise UserError(
                        _("Already one payment selected as home delivery , you can not create multiple home delivery methods."))
        return super(PosPaymentMethod, self).create(vals)

    def write(self, vals):
        methods = self.search_count([('is_home_delivery', '=', True)])
        if 'is_home_delivery' in vals:
            if vals.get('is_home_delivery') == True:
                if methods >= 1:
                    raise UserError(
                        _("Already one payment selected as home delivery , you can not create multiple home delivery methods."))
        return super(PosPaymentMethod, self).write(vals)
