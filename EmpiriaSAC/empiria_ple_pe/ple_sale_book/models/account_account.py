from odoo import _, api, fields, models, tools


class Account(models.Model):
    _inherit = "account.account"

    ple_date_account = fields.Date(
        string="Fecha de cuenta",
        default=fields.Date.today,
    )

    ple_state_account = fields.Selection(
        selection=[
            ("1", "1"),
            ("8", "8"),
            ("9", "9"),
        ],
        string="Estado",
        default="1",
    )

    ple_selection = fields.Selection(
        selection=[],
        string="PLE",
    )
