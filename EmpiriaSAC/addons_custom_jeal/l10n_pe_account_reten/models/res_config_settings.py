from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Configuraciones para retenciones
    is_retention = fields.Boolean(
        string="Habilitar Retención",
        related="company_id.is_retention",
        readonly=False,
        help="Activa la retención para proveedores.",
    )

    percentage_retention = fields.Float(
        string="% Retención",
        related="company_id.percentage_retention",
        readonly=False,
        help="Porcentaje de retención que se aplicará.",
    )

    amount_minimum_retention = fields.Float(
        string="Monto Mínimo para Retención",
        related="company_id.amount_minimum_retention",
        readonly=False,
        help="Monto mínimo necesario para aplicar la retención.",
    )

    journal_retention_id = fields.Many2one(
        comodel_name="account.journal",
        string="Diario Contable",
        related="company_id.journal_retention_id",
        readonly=False,
        help="Diario contable que se utilizará para registrar la retención.",
    )

    account_retention_id = fields.Many2one(
        comodel_name="account.account",
        string="Cuenta Contable",
        related="company_id.account_retention_id",
        readonly=False,
        help="Cuenta contable donde se registrará la retención.",
    )

    document_type_retention_id = fields.Many2one(
        comodel_name="l10n_latam.document.type",
        string="Tipo de Documento",
        related="company_id.document_type_retention_id",
        readonly=False,
        help="Tipo de documento utilizado para la retención.",
    )

    @api.onchange("is_retention")
    def _onchange_is_retention(self):
        """
        Método que se ejecuta al cambiar el valor de 'is_retention'.
        Si la retención está desactivada, se resetean los valores relacionados a la retención.
        """
        if not self.is_retention:
            # Si no se habilita la retención, se reinician los valores a 0
            self.percentage_retention = 0.0
            self.amount_minimum_retention = 0.0
            self.journal_retention_id = self.company_id._get_default_journal_retention()
            self.account_retention_id = False
            self.document_type_retention_id = (
                self.company_id._get_default_document_type_retention()
            )
