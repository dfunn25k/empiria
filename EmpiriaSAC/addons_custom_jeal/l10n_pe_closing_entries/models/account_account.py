from odoo import models, fields


class AccountAccount(models.Model):
    _inherit = "account.account"

    is_closing_account = fields.Boolean(
        string="Es Cuenta de Cierre/Resultado",
        help="Marque esta opción si esta cuenta es una cuenta de resultados que no se debe cerrar, "
        "sino que se utiliza como contrapartida para otras cuentas.",
    )

    closing_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Cuenta de Cierre",
        help="Cuenta utilizada como contrapartida en el asiento de cierre para esta cuenta.",
    )

    detailed_by_product = fields.Boolean(
        string="Producto Detallado",
        default=False,
        help="Si se marca, el asiento de cierre para esta cuenta se generará con una línea "
        "separada para cada producto con saldo.",
    )
