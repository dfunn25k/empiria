from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_home_delivery = fields.Boolean(
        string='Use as Home Delivery',
        help='if you use this journal as home delivery, it will not create any payment entries for that order'
    )
