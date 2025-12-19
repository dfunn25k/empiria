from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError


class AccountJournal(models.Model):
    _inherit = "account.journal"

    # retention_series = fields.Char(
    #     string="Serie",
    #     size=3,
    #     required=True,
    #     help="Serie del documento utilizada en la numeración de comprobantes. Ejemplo: '001'.",
    # )

    retention_sequence = fields.Char(
        string="Secuencia de Retención",
        size=8,
        required=True,
        default="00000001",
        help="Número de secuencia del documento con un tamaño máximo de 8 caracteres. Ejemplo: '00000001'.",
    )

    # ---------------------------------------------------------------------------- #
    #                                 TODO - METODO                                #
    # ---------------------------------------------------------------------------- #
    def create_retention_journals_for_all_companies(self):
        """
        Crea el diario 'Comprobante de retención' para cada compañía en el sistema,
        asegurándose de que no exista previamente un diario con el mismo código ('001').
        El método usa `sudo()` para evitar problemas de permisos en entornos multi-compañía.
        """
        # Obtiene todas las compañías del sistema
        companies = self.env["res.company"].search([])

        # Itera sobre cada compañía para crear el diario de retención si no existe
        for company in companies:
            # Verifica si ya existe un diario con el código '001' en esta compañía
            existing_journal = self.sudo().search(
                [("company_id", "=", company.id), ("code", "=", "001")]
            )

            # Si no existe, crea el nuevo diario
            if not existing_journal:
                self.sudo().create(
                    {
                        "name": "Comprobante de retención",
                        "code": "001",
                        "type": "general",
                        "company_id": company.id,
                    }
                )
