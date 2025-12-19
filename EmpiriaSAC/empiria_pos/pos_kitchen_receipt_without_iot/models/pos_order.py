from odoo import api, fields, models



class PosOrder(models.Model):
    _inherit = "pos.order"

    def _get_fields_for_order_line(self):
        res = super(PosOrder, self)._get_fields_for_order_line()
        res += ['printed_line_id']
        return res
