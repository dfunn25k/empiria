from odoo.tests.common import TransactionCase
import datetime
import base64
import logging
_logger = logging.getLogger(__name__)


class TestBBVAPayment(TransactionCase):
    def setUp(self):
        super().setUp()
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

        self.bbva_bank = self.env['res.bank'].create({
            'name': 'BBVA Banco Continental',
            'bic': 'BBVAPEPL',
            'sunat_bank_code': '11' # '11 - CONTINENTAL'
        })

        self.account_payable = self.env['account.account'].search([
            ('company_id', '=', self.company.id),
            ('account_type', '=', 'liability_payable')
        ], limit=1)

        self.bank_account_bbva_pen = self.env['res.partner.bank'].create({
            'acc_type': 'bank',
            'acc_number': '0011-0333-0100044588',
            'partner_id': self.company.partner_id.id,
            'bank_id': self.bbva_bank.id,
            'currency_id': self.env.ref('base.PEN').id,
            'company_id': self.company.id,
            'allow_out_payment': True,
        })

        self.bank_account_bbva_dol = self.env['res.partner.bank'].create({
            'acc_type': 'bank',
            'acc_number': '0011-0333-0100044599',
            'partner_id': self.company.partner_id.id,
            'bank_id': self.bbva_bank.id,
            'currency_id': self.env.ref('base.USD').id,
            'company_id': self.company.id,
            'allow_out_payment': True,
        })

        self.journal_bbva_PEN = self.env['account.journal'].create({
            'name': 'Test Journal BBVA PEN',
            'type': 'bank',
            'code': 'BBVAPEN',
            'currency_id': self.env.ref('base.PEN').id,
            'bank_account_id': self.bank_account_bbva_pen.id,
            'company_id': self.company.id,
            'bank_id': self.bbva_bank.id,
        })

        self.journal_bbva_DOL = self.env['account.journal'].create({
            'name': 'Test Journal BBVA DOL',
            'type': 'bank',
            'code': 'BBVADOL',
            'currency_id': self.env.ref('base.USD').id,
            'bank_account_id': self.bank_account_bbva_dol.id,
            'company_id': self.company.id,
            'bank_id': self.bbva_bank.id,
        })

        self.supplier1 = self.env['res.partner'].create({
            'name': 'Test Supplier',
            'is_company': True,
            'vat': '20602990797',
            'street': 'Test Street',
            'bank_ids': [(0, 0, {
                'bank_id': self.bbva_bank.id,
                'acc_number': '0011-0310-0100060928',
                'cci': '0111-3100-000100060928',
                'acc_type': 'bank',
            }),],
            'l10n_latam_identification_type_id': self.env.ref('l10n_pe.it_RUC').id,
        })

        self.supplier2 = self.env['res.partner'].create({
            'name': 'Test 2 Supplier',
            'is_company': True,
            'vat': '20602990798',
            'street': 'Test Street 2',
            'bank_ids': [(0, 0, {
                'bank_id': self.bbva_bank.id,
                'acc_number': '0011-0310-0100060929',
                'cci': '0111-3100-000100060928',
                'acc_type': 'bank',
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
            'payment_reference': f'{supplier.name}-{ref.split("-")[-1]}',
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
    
        expected_lines = [line for line in expected_content.splitlines()]
        file_lines = [line for line in file_content.splitlines()]
        
        # Comparar línea por línea
        self.assertEqual(len(expected_lines), len(file_lines), "El número de líneas no coincide")
        
        for i, (expected, actual) in enumerate(zip(expected_lines, file_lines)):
            self.assertEqual(len(actual), 151 if i == 0 else 277, f"La longitud de la línea {i+1} no es la esperada")
            self.assertEqual(len(expected), len(actual), f"La longitud de la línea {i+1} no coincide")
            self.assertEqual(expected, actual, f"El contenido de la línea {i+1} no coincide")

    def test_bbva_payment_pen(self):
        # Este test crea 1 facturas de proveedor, diario en soles
        invoice = self._create_invoice(self.supplier1, 'F400-30020',self.env.ref('base.PEN').id)
        invoice.action_post()

        # Crear el contexto para el asistente de pago
        ctx = {
            'active_model': 'account.move',
            'active_ids': [invoice.id],
            'default_company_id': self.company.id,
        }
        payment_register = self.env['account.payment.register'].with_context(ctx).create({
            'journal_id': self.journal_bbva_PEN.id,
            'company_id': self.company.id,
            'payment_method_line_id': self.journal_bbva_PEN.outbound_payment_method_line_ids[0].id,
        })
        payment = payment_register.action_create_payments()
        
        # 3. Buscar el pago creado
        account_payment = self.env['account.payment'].browse(payment['res_id'])
        self.assertTrue(account_payment, "El pago no se creó correctamente")
        # 4. Crear el pago masivo
        batch_payment = self.env['account.batch.payment'].create({
            'journal_id': self.journal_bbva_PEN.id,
            'payment_method_id': self.journal_bbva_PEN.outbound_payment_method_line_ids[0].payment_method_id.id,
            'payment_ids': [(4, account_payment.id)],
            'batch_type': 'outbound',
            'process_type': 'A',
        })

        batch_payment.generate_txt_suppliers()

        expected_content = "75000110333000100044588PEN000000000023600A{}{}000001N000000000000000000{}\r\n".format(
            ' ' * 9,
            batch_payment.name.ljust(25, ' '),
            ' ' * 50,
        )
        expected_content += "002R20602990797 P00110310000100060928{}000000000023600F{}N{}{}\r\n".format(
            self.supplier1.name.ljust(40, ' ') if len(self.supplier1.name) < 40 else str(self.supplier1.name)[:40],
            str(invoice.payment_reference)[-8:].ljust(12, ' '),
            str(account_payment.name).ljust(40, ' ') if account_payment.name else ' '*40,
            ' ' * 81 + '0' * 32 + ' ' * 18,
        )
        
        self._verify_txt_content(batch_payment, expected_content)

    
    def test_bbva_payment_dollar(self):
        invoice = self._create_invoice(self.supplier2, 'F400-30020', self.env.ref('base.USD').id)
        invoice.action_post()

        ctx = {
            'active_model': 'account.move',
            'active_ids': [invoice.id],
            'default_company_id': self.company.id,
        }
        payment_register = self.env['account.payment.register'].with_context(ctx).create({
            'journal_id': self.journal_bbva_DOL.id,
            'company_id': self.company.id,
            'payment_method_line_id': self.journal_bbva_DOL.outbound_payment_method_line_ids[0].id,
        })
        payment = payment_register.action_create_payments()
        
        account_payment = self.env['account.payment'].browse(payment['res_id'])
        self.assertTrue(account_payment, "El pago no se creó correctamente")
        
        future_date = datetime.date.today() + datetime.timedelta(days=5)
        batch_payment = self.env['account.batch.payment'].create({
            'journal_id': self.journal_bbva_DOL.id,
            'payment_method_id': self.journal_bbva_DOL.outbound_payment_method_line_ids[0].payment_method_id.id,
            'payment_ids': [(4, account_payment.id)],
            'batch_type': 'outbound',
            'process_type': 'F',
            'future_date': future_date,
        })

        batch_payment.generate_txt_suppliers()

        expected_content = "75000110333000100044599USD000000000023600F{} {}000001N000000000000000000{}\r\n".format(
            future_date.strftime('%Y%m%d'),
            batch_payment.name.ljust(25, ' '),
            ' ' * 50,
        )

        expected_content += "002R20602990798 P00110310000100060929{}000000000023600F{}N{}{}\r\n".format(
            self.supplier2.name.ljust(40, ' ') if len(self.supplier2.name) < 40 else str(self.supplier2.name)[:40],
            str(invoice.payment_reference)[-8:].ljust(12, ' '),
            str(account_payment.name).ljust(40, ' ') if account_payment.name else ' '*40,
            ' ' * 81 + '0' * 32 + ' ' * 18,
        )

        self._verify_txt_content(batch_payment, expected_content)

    def test_bbva_payment_two_suppliers(self):
        invoice1 = self._create_invoice(self.supplier1, 'F400-30020', self.env.ref('base.PEN').id)
        invoice2 = self._create_invoice(self.supplier2, 'F400-30021', self.env.ref('base.PEN').id)
        invoice1.action_post()
        invoice2.action_post()

        ctx1 = {
            'active_model': 'account.move',
            'active_ids': [invoice1.id],
            'default_company_id': self.company.id,
        }
        payment_register1 = self.env['account.payment.register'].with_context(ctx1).create({
            'journal_id': self.journal_bbva_PEN.id,
            'company_id': self.company.id,
            'payment_method_line_id': self.journal_bbva_PEN.outbound_payment_method_line_ids[0].id,
        })
        payment1 = payment_register1.action_create_payments()

        ctx2 = {
            'active_model': 'account.move',
            'active_ids': [invoice2.id],
            'default_company_id': self.company.id,
        }
        payment_register2 = self.env['account.payment.register'].with_context(ctx2).create({
            'journal_id': self.journal_bbva_PEN.id,
            'company_id': self.company.id,
            'payment_method_line_id': self.journal_bbva_PEN.outbound_payment_method_line_ids[0].id,
        })
        payment2 = payment_register2.action_create_payments()

        account_payment1 = self.env['account.payment'].browse(payment1['res_id'])
        account_payment2 = self.env['account.payment'].browse(payment2['res_id'])
        self.assertTrue(account_payment1, "El pago no se creó correctamente")
        self.assertTrue(account_payment2, "El pago no se creó correctamente")

        batch_payment = self.env['account.batch.payment'].create({
            'journal_id': self.journal_bbva_PEN.id,
            'payment_method_id': self.journal_bbva_PEN.outbound_payment_method_line_ids[0].payment_method_id.id,
            'payment_ids': [(4, account_payment1.id, 0), (4, account_payment2.id, 0)],
            'batch_type': 'outbound',
            'process_type': 'H',
            'executing_schedule': 'C',
        })

        batch_payment.generate_txt_suppliers()

        expected_content = "75000110333000100044588PEN000000000047200H{}C{}000002N000000000000000000{}\r\n".format(
            ' ' * 8,
            batch_payment.name.ljust(25, ' '),
            ' ' * 50,
        )

        expected_content += "002R20602990797 P00110310000100060928{}000000000023600F{}N{}{}\r\n".format(
            self.supplier1.name.ljust(40, ' ') if len(self.supplier1.name) < 40 else str(self.supplier1.name)[:40],
            str(invoice1.payment_reference)[-8:].ljust(12, ' '),
            str(account_payment1.name).ljust(40, ' ') if account_payment1.name else ' '*40,
            ' ' * 81 + '0' * 32 + ' ' * 18,
        )

        expected_content += "002R20602990798 P00110310000100060929{}000000000023600F{}N{}{}\r\n".format(
            self.supplier2.name.ljust(40, ' ') if len(self.supplier2.name) < 40 else str(self.supplier2.name)[:40],
            str(invoice2.payment_reference)[-8:].ljust(12, ' '),
            str(account_payment2.name).ljust(40, ' ') if account_payment2.name else ' '*40,
            ' ' * 81 + '0' * 32 + ' ' * 18,
        )

        self._verify_txt_content(batch_payment, expected_content)
