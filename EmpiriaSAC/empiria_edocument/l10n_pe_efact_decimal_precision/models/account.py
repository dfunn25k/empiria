from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _prepare_edi_vals_to_export(self):
        res = super(AccountMoveLine, self)._prepare_edi_vals_to_export()

        try:
            if abs(self.price_subtotal - self.quantity * self.currency_id.round(self.price_total / self.quantity)) > 1:
                res.update({
                    'price_unit_after_discount': self.price_unit * (1 - (self.discount / 100.0)),
                    'price_subtotal_unit': self.price_subtotal / self.quantity if self.quantity else 0.0,
                    'price_total_unit': self.price_total / self.quantity if self.quantity else 0.0,
                })

            for tax in self.tax_ids:
                # GRA - Gratuito - Price amount calc
                if tax.l10n_pe_edi_tax_code and tax.l10n_pe_edi_tax_code == '9996':
                    # Inafecto – Retiro por Bonificación - 31
                    if tax.l10n_pe_edi_affectation_reason == '31':
                        price_subtotal_unit = 0.0
                    # Exonerado - Transferencia gratuita - 21
                    elif tax.l10n_pe_edi_affectation_reason == '21':
                        price_subtotal_unit = self.currency_id.round(self.price_total / self.quantity) if self.quantity else 0.0
                    # Gravado – Retiro por premio - 11
                    else:
                        price_subtotal_unit = 0.0
                    price_total_unit = self.currency_id.round(self.price_subtotal / self.quantity) if self.quantity else 0.0
                    res.update({
                        'price_subtotal_unit': price_subtotal_unit,
                        'price_total_unit': price_total_unit,
                        'price_unit_after_discount': 0.0
                    })
                    break
        except:
            pass
        return res
