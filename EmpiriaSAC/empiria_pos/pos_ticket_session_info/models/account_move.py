from odoo import fields, models, api
import json


class AccountMove(models.Model):
    _inherit = "account.move"

    pos_order_change = fields.Monetary(
        string='POS - Vuelto'
    )
