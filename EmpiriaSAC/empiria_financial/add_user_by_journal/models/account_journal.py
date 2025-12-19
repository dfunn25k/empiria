from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    assign_to_ids = fields.Many2many(
        comodel_name='res.users',
        string='Asignado a',
    )
