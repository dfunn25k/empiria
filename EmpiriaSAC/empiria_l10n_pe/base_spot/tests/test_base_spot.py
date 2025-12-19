from odoo.tests import TransactionCase
from odoo.tests.common import Form
from datetime import date

class TestBaseSpot(TransactionCase):

    def setUp(self):
        super(TestBaseSpot, self).setUp()
        self.account_move = self.env['account.move']
        self.account_move_line = self.env['account.move.line']
        self.account_spot_detraction = self.env['account.spot.detraction']
        self.partner = self.env['res.partner'].create({'name': 'Test Partner'})

    def test_01_create_account_spot_detraction(self):
        detraction = self.account_spot_detraction.create({
            'code': '030',
            'name': 'Test Detraction',
            'rate': 8.00,
        })
        self.assertEqual(detraction.code, '030')
        self.assertEqual(detraction.name, 'Test Detraction')
        self.assertEqual(detraction.rate, 8.00)

    def test_02_create_account_move_with_detraction(self):
        detraction = self.account_spot_detraction.create({
            'code': '031',
            'name': 'Another Test Detraction',
            'rate': 12.00,
        })
        
        # Create the invoice directly instead of using a form
        invoice = self.account_move.create({
            'move_type': 'in_invoice',
            'partner_id': self.partner.id,
            'invoice_date': '2024-01-01',
            'detraction_id': detraction.id,
            'operation_type_detraction': '01',
            'voucher_payment_date': date(2024, 9, 18),
            'voucher_number': 'TEST001',
            'invoice_line_ids': [(0, 0, {
                'name': 'Test line',
                'quantity': 1,
                'price_unit': 100,
            })],
        })
        
        self.assertEqual(invoice.detraction_id, detraction)
        self.assertEqual(invoice.operation_type_detraction, '01')
        self.assertEqual(invoice.voucher_payment_date, date(2024, 9, 18))
        self.assertEqual(invoice.voucher_number, 'TEST001')
        
        # Check if the fields are properly set in the move line
        move_line = invoice.invoice_line_ids[0]
        self.assertEqual(move_line.voucher_payment_date, date(2024, 9, 18))
        self.assertEqual(move_line.voucher_number, 'TEST001')
        

    def test_03_onchange_account_move_line(self):
        invoice = self.account_move.create({
            'move_type': 'in_invoice',
            'partner_id': self.partner.id,
            'invoice_date': '2024-01-01',
            'invoice_line_ids': [(0, 0, {
                'name': 'Test line',
                'quantity': 1,
                'price_unit': 100,
            })],
        })
        
        # Use write method on the invoice instead of the line
        invoice.write({
            'voucher_payment_date': date(2024, 9, 19),
            'voucher_number': 'TEST002'
        })
        
        # Check if the fields are updated in the move line
        move_line = invoice.invoice_line_ids[0]
        self.assertEqual(move_line.voucher_payment_date, date(2024, 9, 19))
        self.assertEqual(move_line.voucher_number, 'TEST002')
        
        # Check if the fields are correctly set in the parent move
        self.assertEqual(invoice.voucher_payment_date, date(2024, 9, 19))
        self.assertEqual(invoice.voucher_number, 'TEST002')