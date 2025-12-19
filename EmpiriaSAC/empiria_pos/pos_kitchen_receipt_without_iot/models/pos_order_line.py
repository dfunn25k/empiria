from odoo import api, fields, models



class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    printed_line_id = fields.Char(
        string='It is used to kwnow if was sended to kitchen'
    )
