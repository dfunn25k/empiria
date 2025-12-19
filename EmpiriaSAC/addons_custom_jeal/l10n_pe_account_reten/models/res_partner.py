from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Campo booleano que indica si el socio es un agente de retención autorizado por la ley fiscal.
    is_retention_agent = fields.Boolean(
        string="¿Es Agente de Retención?",
        store=True,
        index=True,
        tracking=True,
        help="Determina si este socio está autorizado como agente de retención según la ley fiscal vigente.",
    )

    # ---------------------------------------------------------------------------- #
    #                            TODO - METODO ONCHANGE                            #
    # ---------------------------------------------------------------------------- #
    @api.onchange("is_retention_agent")
    def _onchange_is_retention_agent(self):
        """
        Este método se activa cuando cambia el valor del campo 'is_retention_agent'.
        Verifica si ya existe un comprobante de retención asociado al socio, genera una excepción para evitar la desmarcación del campo.
        """
        # Buscar comprobantes de retención existentes para este socio
        existing_retention = self.env["account.retention"].search(
            [
                # Filtrar por el socio de la factura (utilizamos '_origin' para manejar el cambio en el contexto onchange)
                ("partner_id", "=", self._origin.id),
                # Considerar solo los estados 'borrador' o 'terminado'
                ("state", "in", ["draft", "terminate"]),
            ],
            limit=1,
        )

        # Si existe un comprobante en uno de los estados válidos, lanzar un error de validación
        if existing_retention:
            raise ValidationError(
                f"No se puede desmarcar, el contacto '{self.name}' ya tiene un comprobante de retención en estado activo o en proceso."
            )
