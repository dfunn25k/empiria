from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    def _get_default_journal_retention(self):
        """
        Obtiene el diario de retención por defecto.
        Si no se encuentra el diario, retorna None.
        """
        return self.env["account.journal"].search([("code", "=", "001")], limit=1)

    def _get_default_document_type_retention(self):
        """
        Obtiene el tipo de documento de retención por defecto.
        Busca el tipo de documento con código '20', que es el estándar para retenciones.
        """
        return self.env["l10n_latam.document.type"].search(
            [("code", "=", "20")], limit=1
        )

    # Configuraciones para retenciones
    is_retention = fields.Boolean(
        string="Habilitar Retención",
        default=False,
        help="Activa la retención para proveedores.",
    )

    percentage_retention = fields.Float(
        sstring="Porcentaje de Retención (%)",
        help="Porcentaje de retención que se aplicará a las facturas de proveedores.",
    )

    amount_minimum_retention = fields.Float(
        string="Monto Mínimo de Retención",
        help="Monto mínimo necesario para que se aplique la retención.",
    )

    journal_retention_id = fields.Many2one(
        comodel_name="account.journal",
        string="Diario de Retención",
        default=_get_default_journal_retention,
        help="Diario contable que se utilizará para registrar las retenciones de proveedores.",
    )

    account_retention_id = fields.Many2one(
        comodel_name="account.account",
        string="Cuenta de Retención",
        help="Cuenta contable donde se registrarán las retenciones aplicadas.",
    )

    document_type_retention_id = fields.Many2one(
        comodel_name="l10n_latam.document.type",
        string="Tipo de Documento de Retención",
        default=_get_default_document_type_retention,
        help="Tipo de documento utilizado para las retenciones (ej. Código 20).",
    )
