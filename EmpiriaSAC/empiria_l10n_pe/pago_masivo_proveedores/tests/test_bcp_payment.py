from odoo.tests.common import TransactionCase
import datetime
import base64
import logging
_logger = logging.getLogger(__name__)


class TestBCPPayment(TransactionCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.company = self.env['res.company'].create({
            'name': 'Test Company',
            'country_id': self.env.ref('base.pe').id,
            'currency_id': self.env.ref('base.PEN').id,
            'vat': '20602990797',
        })

        self.env.ref('base.USD').active = True
        self.env.user.company_id = self.company
        self.env.company = self.company

        chart_template = self.env.ref('l10n_pe.pe_chart_template')
        chart_template.try_loading(company=self.company)

        self.bcp_bank = self.env['res.bank'].create({
            'name': 'BCP',
            'bic': 'BCPLPEPL',
            'sunat_bank_code': '02',
        })

        self.account_payable = self.env['account.account'].search([
            ('company_id', '=', self.company.id),
            ('account_type', '=', 'liability_payable')
        ], limit=1)

        self.bank_account_bcp_pen = self.env['res.partner.bank'].create({
            'acc_type': 'bank',
            'acc_number': '1932239573048',
            'partner_id': self.company.partner_id.id,
            'bank_id': self.bcp_bank.id,
            'currency_id': self.env.ref('base.PEN').id,
            'company_id': self.company.id,
            'allow_out_payment': True,
        })

        self.bank_account_bcp_usd = self.env['res.partner.bank'].create({
            'acc_type': 'bank',
            'acc_number': '1932239573049',
            'partner_id': self.company.partner_id.id,
            'bank_id': self.bcp_bank.id,
            'currency_id': self.env.ref('base.USD').id,
            'company_id': self.company.id,
            'allow_out_payment': True,
        })

        self.journal_bcp_PEN = self.env['account.journal'].create({
            'name': 'Test Journal BBVA PEN',
            'type': 'bank',
            'code': 'BCPPEN',
            'currency_id': self.env.ref('base.PEN').id,
            'bank_account_id': self.bank_account_bcp_pen.id,
            'company_id': self.company.id,
            'bank_id': self.bcp_bank.id,
        })

        self.journal_bcp_usd = self.env['account.journal'].create({
            'name': 'Test Journal BBVA USD',
            'type': 'bank',
            'code': 'BCPUSD',
            'currency_id': self.env.ref('base.USD').id,
            'bank_account_id': self.bank_account_bcp_usd.id,
            'company_id': self.company.id,
            'bank_id': self.bcp_bank.id,
        })

        self.supplier1 = self.env['res.partner'].create({
            'name': 'Test Supplier',
            'is_company': True,
            'vat': '20602990797',
            'street': 'Test Street',
            'bank_ids': [(0, 0, {
                'bank_id': self.bcp_bank.id,
                'acc_number': '1912454696111',
                'cci': '00219100245469611751',
                'acc_type': 'bank',
                'account_type': '001' # campo especifico para el BCP, para saber que tipo de cuenta es 
            }),],
            'l10n_latam_identification_type_id': self.env.ref('l10n_pe.it_RUC').id,
        })

        self.supplier2 = self.env['res.partner'].create({
            'name': 'Test 2 Supplier',
            'is_company': True,
            'vat': '20602990798',
            'street': 'Test Street 2',
            'bank_ids': [(0, 0, {
                'bank_id': self.bcp_bank.id,
                'acc_number': '1912454696112',
                'cci': '00219100245469611752',
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
            'payment_reference': '00000001',
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
    
    def _verify_txt_content(self, batch_payment, expected_content):
        expected_content_in_console = f"Expected content:\n'{expected_content}'"
        _logger.info(expected_content_in_console)
        file_content = base64.b64decode(batch_payment.txt_binary_bank).decode('utf-8')
        file_content_in_console = f"file_content:\n'{file_content}'"
        _logger.info(file_content_in_console)

        # QUIERO VERIFICAR QUE EL CONTENIDO DE LAS LINEAS SEA IGUALES
        self.assertEqual(file_content, expected_content, "El contenido del archivo TXT no es el esperado")
        expected_lines = [line for line in expected_content.splitlines()]     
        file_lines = [line for line in file_content.splitlines()]

        self.assertEqual(len(file_lines), len(expected_lines), "El archivo TXT no tiene el número de líneas esperado")

        for i, (expected, actual) in enumerate(zip(expected_lines, file_lines)):
            if actual[0] == 1:
                self.assertEqual(len(actual), 114)
            elif actual[0] == 2:
                self.assertEqual(len(actual), 197)
            elif actual[0] == 3:
                self.assertEqual(len(actual), 35)

            self.assertEqual(len(expected), len(actual), f"La longitud de la línea {i+1} no coincide")
            self.assertEqual(expected, actual, f"El contenido de la línea {i+1} no coincide")

    def test_bcp_payments_pen(self):
        invoice1 = self._create_invoice(self.supplier1, 'F500-40030', self.env.ref('base.PEN').id)
        invoice2 = self._create_invoice(self.supplier2, 'F500-40031', self.env.ref('base.PEN').id)

        invoice1.action_post()
        invoice2.action_post()

        ctx1 = {
            'active_model': 'account.move',
            'active_ids': [invoice1.id],
            'default_company_id': self.company.id,
        }

        ctx2 = {
            'active_model': 'account.move',
            'active_ids': [invoice2.id],
            'default_company_id': self.company.id,
        }

        payment_register1 = self.env['account.payment.register'].with_context(ctx1).create({
            'journal_id': self.journal_bcp_PEN.id,
            'company_id': self.company.id,
            'payment_method_line_id': self.journal_bcp_PEN.outbound_payment_method_line_ids[0].id,
        })

        payment1 = payment_register1.action_create_payments()

        ctx2 = {
            'active_model': 'account.move',
            'active_ids': [invoice2.id],
            'default_company_id': self.company.id,
        }

        payment_register2 = self.env['account.payment.register'].with_context(ctx2).create({
            'journal_id': self.journal_bcp_PEN.id,
            'company_id': self.company.id,
            'payment_method_line_id': self.journal_bcp_PEN.outbound_payment_method_line_ids[0].id,
        })

        payment2 = payment_register2.action_create_payments()

        account_payment1 = self.env['account.payment'].browse(payment1['res_id'])
        account_payment2 = self.env['account.payment'].browse(payment2['res_id'])
        self.assertTrue(account_payment1, "El pago no se creó correctamente")
        self.assertTrue(account_payment2, "El pago no se creó correctamente")

        batch_payment = self.env['account.batch.payment'].create({
            'journal_id': self.journal_bcp_PEN.id,
            'payment_method_id': self.journal_bcp_PEN.outbound_payment_method_line_ids[0].payment_method_id.id,
            'payment_ids': [(4, account_payment1.id, 0), (4, account_payment2.id, 0)],
            'batch_type': 'outbound',
        })

        batch_payment.generate_txt_suppliers()

        expected_content = "1000002{}C00011932239573048       00000000000472.00{}N{}\r\n".format(
            batch_payment.date.strftime('%Y%m%d'),
            batch_payment.name.ljust(40, ' '),
            # la suma de los números de cuenta de los proveedores y la de cargo, sin contar el número de sucursal
            str(2239573048 + 2454696111 + 2454696112)[-15:].rjust(15, '0')
        )

        expected_content += "2C1912454696111       1620602990797    {}{}{}000100000000000236.00S\r\n".format(
            self.supplier1.name.ljust(75, ' '),
            batch_payment.name[:40].ljust(40, ' '),
            batch_payment.name[:20].ljust(20, ' '),
        )
        expected_content += "2C1912454696112       1620602990798    {}{}{}000100000000000236.00S\r\n".format(
            self.supplier2.name.ljust(75, ' '),
            batch_payment.name[:40].ljust(40, ' '),
            batch_payment.name[:20].ljust(20, ' '),

        )
        expected_content += "3F00000000000000100000000000236.00\r\n"
        expected_content += "3F00000000000000100000000000236.00\r\n"

        self._verify_txt_content(batch_payment, expected_content)

    def test_bcp_payments_usd(self):
        invoice = self._create_invoice(self.supplier1, 'F500-40030', self.env.ref('base.USD').id)
        invoice.action_post()

        ctx = {
            'active_model': 'account.move',
            'active_ids': [invoice.id],
            'default_company_id': self.company.id,
        }

        payment_register = self.env['account.payment.register'].with_context(ctx).create({
            'journal_id': self.journal_bcp_usd.id,
            'company_id': self.company.id,
            'payment_method_line_id': self.journal_bcp_usd.outbound_payment_method_line_ids[0].id,
        })
        payment = payment_register.action_create_payments()

        account_payment = self.env['account.payment'].browse(payment['res_id'])
        self.assertTrue(account_payment, "El pago no se creó correctamente")

        batch_payment = self.env['account.batch.payment'].create({
            'journal_id': self.journal_bcp_usd.id,
            'payment_method_id': self.journal_bcp_usd.outbound_payment_method_line_ids[0].payment_method_id.id,
            'payment_ids': [(4, account_payment.id, 0)],
            'batch_type': 'outbound',
        })

        batch_payment.generate_txt_suppliers()

        expected_content = "1000001{}C10011932239573049       00000000000236.00{}N{}\r\n".format(
            batch_payment.date.strftime('%Y%m%d'),
            batch_payment.name.ljust(40, ' '),
            # la suma de los números de cuenta de los proveedores y la de cargo, sin contar el número de sucursal
            str(2239573049 + 2454696111)[-15:].rjust(15, '0')
        )

        expected_content += "2C1912454696111       1620602990797    {}{}{}100100000000000236.00S\r\n".format(
            self.supplier1.name.ljust(75, ' '),
            batch_payment.name[:40].ljust(40, ' '),
            batch_payment.name[:20].ljust(20, ' '),
        )

        expected_content += "3F00000000000000100000000000236.00\r\n"

        self._verify_txt_content(batch_payment, expected_content)
