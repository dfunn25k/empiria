from odoo import _, fields, models


class AccountAccount(models.Model):
    """
    Extiende el modelo contable para definir si una cuenta requiere
    una distribución analítica obligatoria.
    """

    _inherit = "account.account"

    requires_analytic = fields.Boolean(
        string="Requiere cuenta analítica",
        help=(
            "Si se marca, todas las líneas de asientos contables "
            "que utilicen esta cuenta deberán tener una distribución "
            "analítica obligatoria cuya suma sea igual al 100 %."
        ),
    )
