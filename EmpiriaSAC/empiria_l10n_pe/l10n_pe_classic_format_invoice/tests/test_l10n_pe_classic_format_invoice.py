from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools import test_reports


@tagged('post_install', '-at_install')
class TestL10nPEClassicFormatInvoice(TransactionCase):

    def setUp(self):
        super().setUp()
        self.product_template_obj = self.env['product.template']
        self.partner_obj = self.env['res.partner']
        self.payment_term_obj = self.env['account.payment.term']
        self.account_move_obj = self.env['account.move']
        self.ir_actions_report_obj = self.env['ir.actions.report']

    def test_print_l10n_pe_classic_invoice_report(self):
        product_template = self.product_template_obj.create({
            'name': 'Suscripción Mensual',
            'type': 'service',
            'list_price': 1500,
            'taxes_id': [(6, 0, [self.env.ref('l10n_pe.sale_tax_igv_18').id])],
            'l10n_pe_withhold_code': '037',
            'sale_ok': True,
            'purchase_ok': True,
        })

        partner = self.partner_obj.create({
            'name': 'Burima SAC',
            'street': 'Calle siete 666',
            'vat': '20551583041',
            'l10n_latam_identification_type_id': self.env.ref('l10n_pe.it_RUC').id,
            'company_type': 'company',
        })

        payment_term = self.payment_term_obj.create({
            'name': '30% Ahora, Balance en 60 Días',
            'note': '30% Ahora, Balance en 60 Días',
            'display_on_invoice': True,
            'line_ids': [
                (0, 0, {'value': 'balance', 'days': 90}),
                (0, 0, {'value': 'percent', 'value_amount': 20.000000, 'days': 60}),
                (0, 0, {'value': 'percent', 'value_amount': 12.000000, 'days': 0, 'l10n_pe_is_detraction_retention': True}),
            ],
        })

        invoice = self.account_move_obj.create({
            'partner_id': partner.id,
            'move_type': 'out_invoice',
            'invoice_date': '2024-04-11',
            'invoice_line_ids': [(0, 0, {
                'product_id': product_template.product_variant_id.id,
                'quantity': 1,
                'price_unit': 1800,
            })],
            'invoice_payment_term_id': payment_term.id,
        })

        report_action = self.env.ref('classic_format_invoice.account_invoices_classic')
        pdf_content, _ = self.ir_actions_report_obj._render_qweb_pdf(
            report_action,
            res_ids=invoice.ids,
        )

        self.assertTrue(pdf_content)
