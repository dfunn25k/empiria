from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.constrains("analytic_distribution", "account_id")
    def _check_analytic_distribution_required(self):
        """
        Valida la distribución analítica en las líneas contables.

        1. Si la cuenta (account_id) tiene 'requires_analytic' = True:
           - Asegura que 'analytic_distribution' no esté vacío.
           - Asegura que la suma de 'analytic_distribution' sea 100%.

        2. Si 'requires_analytic' = False, no se hace ninguna validación.
        """

        # Obtenemos la precisión decimal para comparaciones seguras
        precision = self.env["decimal.precision"].precision_get("Account")

        # Optimizacion: filtramos solo las líneas que nos interesan
        lines_to_check = self.filtered(
            lambda line: line.account_id and line.account_id.requires_analytic
        )

        for line in lines_to_check:
            # 1. Si se requiere y está vacío -> Error
            if not line.analytic_distribution:
                raise ValidationError(
                    _(
                        "La línea con la cuenta '%(account)s' requiere una "
                        "distribución analítica, pero no se ha proporcionado ninguna."
                    )
                    % {"account": line.account_id.display_name, "line_id": line.id}
                )

            # 2. Si se requiere y no está vacío, validamos la suma (tu lógica)
            total_percent = sum(
                float(percentage) for percentage in line.analytic_distribution.values()
            )

            # Usamos float_is_zero para comparar decimales de forma segura
            if not float_is_zero(total_percent - 100.0, precision_digits=precision):
                raise ValidationError(
                    _(
                        "La distribución analítica para la cuenta '%(account)s'"
                        "debe sumar 100%%. Total actual: %(total).2f%%"
                    )
                    % {
                        "account": line.account_id.display_name,
                        "line_id": line.id,
                        "total": total_percent,
                    }
                )
