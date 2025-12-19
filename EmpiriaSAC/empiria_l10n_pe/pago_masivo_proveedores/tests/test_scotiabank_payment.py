from odoo.tests.common import TransactionCase
import datetime
import base64
import logging
_logger = logging.getLogger(__name__)


class TestScotiabankPayment(TransactionCase):

    def setUp(self):
        super(TestScotiabankPayment, self).setUp()
        self.maxDiff = None
        self.company = self.env['res.company'].create({
            'name': 'Test Company ',
            'country_id': self.env.ref('base.pe').id,
            'currency_id': self.env.ref('base.PEN').id,
            'vat': '20602990797',
        })

        self.env.ref('base.USD').active = True
        self.env.user.company_id = self.company
        self.env.company = self.company

        chart_template = self.env.ref('l10n_pe.pe_chart_template')
        chart_template.try_loading(company=self.company)

        self.scotia_bank = self.env['res.bank'].create({
            'name': 'Scotiabank',
            'bic': 'BSUDPEPL',
            'sunat_bank_code': '09'
        })

        self.account_payable = self.env['account.account'].search([
            ('company_id', '=', self.company.id),
            ('account_type', '=', 'liability_payable')
        ], limit=1)

        self.bank_account_scotia_pen = self.env['res.partner.bank'].create({
            'acc_type': 'bank',
            'acc_number': '0011-0333-0100044588',
            'partner_id': self.company.partner_id.id,
            'bank_id': self.scotia_bank.id,
            'currency_id': self.env.ref('base.PEN').id,
            'company_id': self.company.id,
            'allow_out_payment': True,
        })

        self.bank_account_scotia_usd = self.env['res.partner.bank'].create({
            'acc_type': 'bank',
            'acc_number': '0011-0333-0100044599',
            'partner_id': self.company.partner_id.id,
            'bank_id': self.scotia_bank.id,
            'currency_id': self.env.ref('base.USD').id,
            'company_id': self.company.id,
            'allow_out_payment': True,
        })

        self.journal_scotia_pen = self.env['account.journal'].create({
            'name': 'Test Journal Scotiabank PEN',
            'type': 'bank',
            'code': 'PENSCOTIA',
            'company_id': self.company.id,
            'bank_account_id': self.bank_account_scotia_pen.id,
            'currency_id': self.env.ref('base.PEN').id,
        })

        self.journal_scotia_usd = self.env['account.journal'].create({
            'name': 'Test Journal Scotiabank USD',
            'type': 'bank',
            'code': 'USDSCOTIA',
            'company_id': self.company.id,
            'bank_account_id': self.bank_account_scotia_usd.id,
            'currency_id': self.env.ref('base.USD').id,
        })

        self.supplier1 = self.env['res.partner'].create({
            'name': 'Test Supplier',
            'is_company': True,
            'vat': '20602990797',
            'street': 'Test Street',
            'email': 'test@gmail.com',
            'bank_ids': [(0, 0, {
                'bank_id': self.scotia_bank.id,
                'acc_number': '0009944702',
                'cci': '01113100000100060928',
                'acc_type': 'bank',
                'account_type': '001'
            }),],
            'l10n_latam_identification_type_id': self.env.ref('l10n_pe.it_RUC').id,
        })

        self.supplier2 = self.env['res.partner'].create({
            'name': 'Test 2 Supplier',
            'is_company': True,
            'vat': '20602990798',
            'street': 'Test Street 2',
            'bank_ids': [(0, 0, {
                'bank_id': self.scotia_bank.id,
                'acc_number': '00009944703',
                'cci': '0111-3100-000100060928',
                'acc_type': 'bank',
                'account_type': '001'
            }),],
            'l10n_latam_identification_type_id': self.env.ref('l10n_pe.it_RUC').id,
        })


        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'list_price': 100.0,
            'standard_price': 80.0,
            'type': 'service',
        })


    def _create_invoice(self, supplier, ref, currency_id=False):
        return self.env['account.move'].with_company(self.company).create({
            'move_type': 'in_invoice',  # Especificar el tipo de movimiento
            'partner_id': supplier.id,
            'ref': ref,
            'invoice_date': datetime.date.today(),
            'date': datetime.date.today(),
            'payment_reference': f'0001',
            'invoice_date_due': datetime.date.today(),
            'l10n_latam_document_type_id': self.env.ref('l10n_pe.document_type01').id,  # Factura
            'l10n_latam_document_number': ref,
            'currency_id': currency_id,
            'partner_bank_id': supplier.bank_ids[0].id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 2.0,
                'price_unit': 100.0,
                'name': self.product.name,  # Agregar descripción
            })]
        })

    def _verify_txt_content(self, batch_payment, expected):
        _logger.info("Expected:\n'%s'", expected)
        content = base64.b64decode(batch_payment.txt_binary_bank).decode('utf-8')
        _logger.info("Content:\n'%s'", content)

        expected_lines = [line for line in expected.splitlines()]
        content_lines = [line for line in content.splitlines()]

        for i, (expected_line, content_line) in enumerate(zip(expected_lines, content_lines)):
            self.assertEqual(len(content_line), 190, f'La longitud de la línea {i+1} no es correcta')
            self.assertEqual(expected_line, content_line, f'El contenido de la línea {i+1} no coincide')

    
    def test_scotiabank_payment_pen(self):
        invoice = self._create_invoice(self.supplier1, 'F001-0001', self.env.ref('base.PEN').id)
        invoice.action_post()

        ctx1 = {
            'active_model': 'account.move',
            'active_ids': [invoice.id],
            'default_company_id': self.company.id,
        }
        
        payment_wizard = self.env['account.payment.register'].with_context(ctx1).create({
            'journal_id': self.journal_scotia_pen.id,
            'company_id': self.company.id,
            'payment_method_line_id': self.journal_scotia_pen.outbound_payment_method_line_ids[0].id,
        })

        payment = payment_wizard.action_create_payments()
        account_payment = self.env['account.payment'].browse(payment['res_id'])
        self.assertEqual(account_payment.journal_id, self.journal_scotia_pen)

        batch_payment = self.env['account.batch.payment'].create({
            'journal_id': self.journal_scotia_pen.id,
            'payment_method_id': self.journal_scotia_pen.outbound_payment_method_line_ids[0].payment_method_id.id,
            'payment_ids': [(4, account_payment.id)],
            'batch_type': 'outbound',
        })

        batch_payment.generate_txt_suppliers()

        expected_content = "20602990797{}{}{}{}20009944702S{}011131000001000609280001\r\n".format(
            self.supplier1.name.ljust(60, ' '),
            account_payment.ref.rjust(14, ' '),
            invoice.date.strftime('%Y%m%d'),
            f"{invoice.amount_total:.2f}".replace('.', '').rjust(11, '0'),
            self.supplier1.email[:50].ljust(50, ' ')
        )

        self._verify_txt_content(batch_payment, expected_content)


    def test_scotiabank_payment_usd(self):
        invoice = self._create_invoice(self.supplier1, 'F001-0001', self.env.ref('base.USD').id)
        invoice.action_post()

        ctx1 = {
            'active_model': 'account.move',
            'active_ids': [invoice.id],
            'default_company_id': self.company.id,
        }

        payment_wizard = self.env['account.payment.register'].with_context(ctx1).create({
            'journal_id': self.journal_scotia_usd.id,
            'company_id': self.company.id,
            'payment_method_line_id': self.journal_scotia_usd.outbound_payment_method_line_ids[0].id,
        })

        payment = payment_wizard.action_create_payments()
        account_payment = self.env['account.payment'].browse(payment['res_id'])
        self.assertEqual(account_payment.journal_id, self.journal_scotia_usd)

        batch_payment = self.env['account.batch.payment'].create({
            'journal_id': self.journal_scotia_usd.id,
            'payment_method_id': self.journal_scotia_usd.outbound_payment_method_line_ids[0].payment_method_id.id,
            'payment_ids': [(4, account_payment.id)],
            'batch_type': 'outbound',
        })

        batch_payment.generate_txt_suppliers()

        expected_content = "20602990797{}{}{}{}20009944702S{}011131000001000609280101\r\n".format(
            self.supplier1.name.ljust(60, ' '),
            account_payment.ref.rjust(14, ' '),
            invoice.date.strftime('%Y%m%d'),
            f"{invoice.amount_total:.2f}".replace('.', '').rjust(11, '0'),
            self.supplier1.email[:50].ljust(50, ' ')
        )

        self._verify_txt_content(batch_payment, expected_content)