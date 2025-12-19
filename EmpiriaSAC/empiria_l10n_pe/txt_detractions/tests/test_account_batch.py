from odoo.tests import common
from odoo.tests.common import tagged
from odoo.exceptions import UserError
from datetime import date

@tagged('post_install', '-at_install')
class TestAccountBatch(common.TransactionCase):

    def setUp(self):
        super().setUp()
        
        self.company = self.env['res.company'].create({
            'name': 'Test Company',
            'vat': '123456789',
        })
        
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'vat': '123456789',
        })
        
        self.journal = self.env['account.journal'].create({
            'name': 'Test Journal',
            'type': 'bank',
            'code': 'TJ01',
        })
        
        self.payment_method = self.env['account.payment.method'].create({
            'name': 'Test Payment Method',
            'payment_type': 'outbound', 
            'code': 'TEST_CODE'
        })
        
        self.payment_method_line = self.env['account.payment.method.line'].create({
            'name': 'Test Payment Method Line',
            'payment_method_id': self.payment_method.id,  
        })
        
        self.batch_payment = self.env['account.batch.payment'].create({
            'lot_number': 'Lote 001',
            'payment_method_line_detraction': self.payment_method_line.id,  
            'payment_method_id': self.payment_method.id,
            'journal_id': self.journal.id 
        })

    def test_compute_filter_detraction(self):
        payment = self.env['account.payment'].create({
            'amount': 100.0,
            'partner_id': self.partner.id,
            'payment_method_line_id': self.payment_method_line.id,
            'batch_payment_id': self.batch_payment.id,
        })
        
        self.batch_payment.payment_ids = [(4, payment.id)]
        
        self.batch_payment._compute_filter_detraction()
        
        self.assertEqual(self.batch_payment.payment_method_line_detraction, self.payment_method_line)
        self.assertEqual(self.batch_payment.payment_method_name, self.payment_method_line.name)

    def test_generate_detraction(self):
        invoice = self.env['account.move'].create({
            'partner_id': self.partner.id,
            'move_type': 'in_invoice',
            'invoice_date': '2024-01-01',
            'state': 'posted',
        })
        
        payment = self.env['account.payment'].create({
            'amount': 100.0,
            'partner_id': self.partner.id,
            'payment_method_line_id': self.payment_method_line.id,
            'batch_payment_id': self.batch_payment.id,
            'reconciled_bill_ids': [(6, 0, [invoice.id])]
        })

        self.batch_payment.payment_ids = [(4, payment.id)]
        
        self.batch_payment.generate_detraction()
        
        self.assertTrue(self.batch_payment.txt_binary)
