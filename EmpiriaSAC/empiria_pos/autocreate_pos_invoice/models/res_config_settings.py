from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_always_move_account = fields.Boolean(
        related='pos_config_id.always_move_account',
        readonly=False
    )
    pos_ticket_user_id = fields.Many2one(
        related='pos_config_id.ticket_user_id',
        readonly=False
    )
    pos_invoice_journal_id = fields.Many2one(
        related='pos_config_id.invoice_journal_id',
        readonly=False,
        domain=False
    )
    pos_ticket_journal_id = fields.Many2one(
        related='pos_config_id.ticket_journal_id',
        readonly=False,
        domain=False
    )
