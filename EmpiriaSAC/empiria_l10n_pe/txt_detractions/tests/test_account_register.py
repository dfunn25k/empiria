from odoo.tests import common
from odoo.tests.common import tagged
from datetime import *

@tagged('post_install', '-at_install')
class TestAccountPaymentRegister(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({'name': 'Partner for Payment'})
        self.payment_method_detraction = self.env['account.payment.method'].create({
            'name': 'Detracción',
            'code': 'DET',
            'payment_type': 'outbound',
        })

        self.journal = self.env['account.journal'].create({
            'name': 'Diario de Ventas Prueba',
            'type': 'sale', 
            'code': 'SL',
            'inbound_payment_method_line_ids': [(0, 0, {
                'name': 'Inbound Method',
                'payment_type': 'inbound',
                'payment_method_id': self.payment_method_detraction.id,
            })],
            'outbound_payment_method_line_ids': [(0, 0, {
                'name': 'Outbound Method',
                'payment_type': 'outbound',
                'payment_method_id': self.payment_method_detraction.id,
            })],
        })

        self.product_with_detraction = self.env['product.product'].create({
            'name': 'Producto Detracción',
            'l10n_pe_withhold_percentage': 10.0  
        })

        self.account_move = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'journal_id': self.journal.id,
            'partner_id': self.partner.id,
            'invoice_date': date.today(),
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product_with_detraction.id,
                'quantity': 1,
                'price_unit': 100.0
            })]
        })
        self.account_move.action_post()  

    def test_filter_detraction(self):
        payment_register = self.env['account.payment.register'].with_context(active_ids=self.account_move.ids).create({
            'journal_id': self.journal.id,
        })

        payment_register._compute_filter_detraction()

        self.assertTrue(payment_register.filter_detraction)

    def test_calculate_detraction_register(self):
        payment_register = self.env['account.payment.register'].with_context(active_ids=self.account_move.ids).create({
            'journal_id': self.journal.id,
        })

        payment_register.calculate_detraction_register()

        expected_amount = round(self.account_move.amount_total * 0.10)  
        self.assertEqual(payment_register.amount, expected_amount)

