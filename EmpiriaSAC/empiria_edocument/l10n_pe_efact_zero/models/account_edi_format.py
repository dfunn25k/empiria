from odoo import models


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    def _l10n_pe_edi_get_edi_values(self, invoice):
        values = super(AccountEdiFormat, self)._l10n_pe_edi_get_edi_values(invoice)
        invoice_line_vals_list = []
        new_index = 1
        for line_vals in values['invoice_line_vals_list']:
            if line_vals['line'].price_subtotal > 0:
                new_line = line_vals.copy()
                new_line['index'] = new_index
                invoice_line_vals_list.append(new_line)
                new_index += 1
        values['invoice_line_vals_list'] = invoice_line_vals_list
        return values
        