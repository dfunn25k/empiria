from odoo import api, fields, models



class PosConfig(models.Model):
    _inherit = 'pos.config'

    allow_kitchens_receipt = fields.Boolean(
        string='Allow Kitchen Receipt', 
        default=True
    )
    use_multi_printer = fields.Boolean(
        string='Use multi printer', 
        default=False
    )