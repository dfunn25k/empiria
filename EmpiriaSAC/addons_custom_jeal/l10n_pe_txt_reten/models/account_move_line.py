from odoo import _, api, fields, models, tools


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def action_generate_txt_pdt_626(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "retention.file.txt",
            "view_mode": "form",
            "view_id": self.env.ref(
                "l10n_pe_txt_reten.view_retention_file_txt_form"
            ).id,
            "context": {
                "default_record_ids": self.ids,  # Pasa los registros seleccionados al wizard
                "default_year": str(
                    fields.Date.today().year
                ),  # Define el año actual por defecto
                "default_period": str(
                    fields.Date.today().month
                ),  # Define el mes actual por defecto
            },
        }
