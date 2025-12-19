from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError

# Definir estados de solo lectura para reutilización
READONLY_FIELD_STATES = {
    state: [("readonly", True)] for state in {"terminate", "cancel"}
}


class AccountRetention(models.Model):
    _inherit = "account.retention"

    company_currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="company_id.currency_id",
        string="Moneda de la Compañía",
        required=True,
        store=True,
        readonly=False,
        precompute=True,
        states=READONLY_FIELD_STATES,
    )

    amount_total = fields.Monetary(
        string="Monto a Retener",
        store=True,
        readonly=True,
        default=0.0,
        compute="_compute_total_retention",
        currency_field="company_currency_id",
    )

    amount_total_converted = fields.Monetary(
        string="Monto Total Convertido",
        store=True,
        readonly=True,
        required=True,
        default=0.0,
        compute="_compute_total_retention",
        currency_field="company_currency_id",
    )

    # ---------------------------------------------------------------------------- #
    #                               TODO - CAMPO LINE                              #
    # ---------------------------------------------------------------------------- #
    retention_line_ids = fields.One2many(
        comodel_name="account.retention.line",
        inverse_name="retention_id",
        string="Líneas de Retención",
        help="Registra las líneas asociadas a la retención actual.",
        states=READONLY_FIELD_STATES,
        auto_join=True,
        readonly=False,
    )

    # ---------------------------------------------------------------------------- #
    #                             TODO - METODO COMPUTE                            #
    # ---------------------------------------------------------------------------- #
    @api.depends(
        "retention_line_ids.amount_total_converted", "retention_line_ids.amount_rt"
    )
    def _compute_total_retention(self):
        """
        Calcula los totales del comprobante en función de los montos de las líneas de retención,
        asegurando que las líneas de retención no se repitan al sumar.
        """
        for record in self:
            # Usa un diccionario para almacenar el Importe Total por factura
            unique_retention_amounts = {}

            for line in record.retention_line_ids:
                invoice_id = line.invoice_id.id

                # Solo agregar la línea si no hemos sumado para esta factura antes
                if invoice_id not in unique_retention_amounts:
                    unique_retention_amounts[invoice_id] = {
                        "amount_total_converted": line.amount_total_converted,
                    }

            # Calcula el total en moneda original sumando los montos de retención de líneas únicas
            record.amount_total = round(
                sum(record.retention_line_ids.mapped("amount_rt") or [0.0]), 2
            )

            # Calcula el total convertido sumando los montos convertidos de líneas únicas
            record.amount_total_converted = round(
                sum(
                    item["amount_total_converted"]
                    for item in unique_retention_amounts.values()
                ),
                2,
            )
