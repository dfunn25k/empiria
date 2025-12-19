from odoo import fields, models

class PosConfig(models.Model):
    _inherit = 'pos.config'
    
    always_move_account = fields.Boolean(
        string='Create seat for each ticket',
        help='If this field is active, Odoo will try to generate an entry for each sale whose total amount is equal to or greater than the one set in the' 
        '"Amount to Bill" field and not only for invoices, in this way each sale will have its accounting entry'
    )
    ticket_user_id = fields.Many2one(
        comodel_name='res.partner',
        string='Default user'
    )
    invoice_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal Invoice'  
    )
    ticket_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal Tickets'
    )