from odoo.tests.common import TransactionCase
import time


class TestAmountToText(TransactionCase):

    def setUp(self):
        super(TestAmountToText, self).setUp()
        self.invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'currency_id': self.env.ref('base.PEN').id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Test product',
                'quantity': 1,
                'price_unit': 123.45,
            })],
        })

    def test_amount_to_text(self):
        amount_in_words = self.invoice._amount_to_text()
        self.assertEqual(amount_in_words, "CIENTO CUARENTA Y CINCO Y 67/100 SOLES")

    def test_amount_without_decimals(self):
        self.invoice.amount_total = 100.00
        self.assertEqual(self.invoice._amount_to_text(), "CIEN Y 00/100 SOLES")

    def test_amount_with_exact_decimals(self):
        self.invoice.amount_total = 100.10
        self.assertEqual(self.invoice._amount_to_text(), "CIEN Y 10/100 SOLES")

    def test_amount_with_high_decimals(self):
        self.invoice.amount_total = 123.99
        self.assertEqual(self.invoice._amount_to_text(), "CIENTO VEINTITRÉS Y 99/100 SOLES")

    def test_amount_in_usd(self):
        self.invoice.currency_id = self.env.ref('base.USD')
        self.invoice.amount_total = 100.50
        self.assertEqual(self.invoice._amount_to_text(), "CIEN Y 50/100 DOLLARS")

    def test_amount_in_usd_with_exact_decimals(self):
        self.invoice.currency_id = self.env.ref('base.USD')
        self.invoice.amount_total = 100.00
        self.assertEqual(self.invoice._amount_to_text(), "CIEN Y 00/100 DOLLARS")

    def test_amount_in_usd_with_high_decimals(self):
        self.invoice.currency_id = self.env.ref('base.USD')
        self.invoice.amount_total = 123.99
        self.assertEqual(self.invoice._amount_to_text(), "CIENTO VEINTITRÉS Y 99/100 DOLLARS")

    def test_large_amount(self):
        self.invoice.amount_total = 1234567.89
        expected = "UN MILLÓN DOSCIENTOS TREINTA Y CUATRO MIL QUINIENTOS SESENTA Y SIETE Y 89/100 SOLES"
        self.assertEqual(self.invoice._amount_to_text(), expected)

    def test_zero_amount(self):
        self.invoice.amount_total = 0.00
        self.assertEqual(self.invoice._amount_to_text(), "CERO Y 00/100 SOLES")

    def test_performance(self):
        start_time = time.time()
        self.invoice.amount_total = 1234567890.99
        self.invoice._amount_to_text()
        duration = time.time() - start_time
        self.assertLess(duration, 1)
