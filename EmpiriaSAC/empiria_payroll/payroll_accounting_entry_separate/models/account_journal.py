from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    def _get_default_account_domain(self):
        return """[
            ('deprecated', '=', False),
            ('company_id', '=', company_id),
            ('account_type', 'not in', ('asset_receivable', 'liability_payable')),
            ('account_type', 'in', ('asset_cash', 'liability_credit_card') if type == 'bank'
                                   else ('asset_cash',) if type == 'cash'
                                   else ('income',) if type == 'sale'
                                   else ('expense',) if type in ('purchase', 'general')
                                   else ())
        ]"""

    default_account_id = fields.Many2one(
        domain=_get_default_account_domain
    )
