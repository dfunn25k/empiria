from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_l10n_latam_documents_domain(self):
        self.ensure_one()
        result = super()._get_l10n_latam_documents_domain()
        if self.company_id.country_id.code != "PE" or not self.journal_id.l10n_latam_use_documents or self.journal_id.type != "sale":
            return result
        result.append(("code", "in", ("01", "03", "07", "08", "20", "40")))
        if self.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code != '6' and self.move_type == 'out_invoice':
            result.append(('id', 'in', (
                self.env.ref('l10n_pe.document_type08b')
                | self.env.ref('l10n_pe.document_type02')
                | self.env.ref('l10n_pe.document_type07b')
            ).ids))
        return result
