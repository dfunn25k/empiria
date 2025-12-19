from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError

# Definir los estados en los que los campos no serán de solo lectura
READONLY_FIELD_STATES = {state: [("readonly", False)] for state in {"draft"}}


class AccountMove(models.Model):
    _inherit = "account.move"

    # Indica si el socio (partner) es un agente de retención autorizado
    is_retention_agent = fields.Boolean(
        string="¿Es Agente de Retención?",
        related="partner_id.is_retention_agent",
        store=True,
        tracking=True,
        states=READONLY_FIELD_STATES,
        help="Determina si el socio es considerado un agente de retención autorizado por la ley. "
        "Este campo se muestra solo en las facturas de proveedores.",
    )

    # Indica si la factura tiene retención aplicada
    has_retention = fields.Boolean(
        string="¿Tiene Retención?",
        store=True,
        default=False,
        tracking=True,
        help="Especifica si este movimiento contable tiene una retención aplicada. "
        "Este valor se actualiza automáticamente según el estado de 'Es Agente de Retención' del socio.",
    )

    # ---------------------------------------------------------------------------- #
    #                            TODO - METODO ONCHANGE                            #
    # ---------------------------------------------------------------------------- #
    @api.onchange("is_retention_agent")
    def _onchange_has_retention(self):
        """
        Actualiza el campo 'has_retention' según el estado de 'is_retention_agent'.
        Si se intenta desmarcar y ya existe un comprobante de retención en proceso para el socio,
        se lanza una excepción.
        """
        # Verificar si el socio actual es agente de retención
        partner_is_retention_agent = self.partner_id.is_retention_agent

        # Verificar si se intenta desmarcar el campo 'is_retention_agent'
        if partner_is_retention_agent and not self.is_retention_agent:
            # Comprobar si ya existe un comprobante de retención en proceso para este socio
            existing_retention = self.env["account.retention"].search(
                [
                    # Socio relacionado con la retención
                    ("partner_id", "=", self.partner_id.id),
                    # Estados 'borrador' o 'terminado'
                    ("state", "in", ["draft", "terminate"]),
                ],
                limit=1,
            )
            # Lanzar excepción si existe un comprobante de retención en proceso
            if existing_retention:
                raise ValidationError(
                    f"No se puede desmarcar, el proveedor '{self.partner_id.name}' ya tiene un comprobante de retención en proceso."
                )

        # Asignar 'has_retention' según el valor de 'is_retention_agent'
        self.has_retention = bool(self.is_retention_agent)
