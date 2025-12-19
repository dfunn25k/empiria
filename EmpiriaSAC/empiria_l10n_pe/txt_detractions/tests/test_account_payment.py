from odoo.tests import common
from odoo.tests.common import tagged
from datetime import date

@tagged('post_install', '-at_install')
class TestAccountPayment(common.TransactionCase):

    def setUp(self):
        super().setUp()
        
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'vat': '123456'
        })
        
        self.journal = self.env['account.journal'].create({
            'name': 'Test Journal',
            'type': 'bank',
            'code': 'TJ01'
        })
        
        self.product = self.env['product.product'].create({
            'name': 'Producto Test',
            'uom_po_id': self.env.ref('uom.product_uom_kgm').id,
            'uom_id': self.env.ref('uom.product_uom_kgm').id,
            'lst_price': 1000.0,
        })
        
        self.invoice = self.env['account.move'].create({
            'partner_id': self.partner.id,
            'journal_id': self.env['account.journal'].search([('type', '=', 'sale')], limit=1).id,
            'currency_id': self.env['res.currency'].search([('name', '=', 'PEN')], limit=1).id,
            'invoice_date': date.today(),
            'l10n_latam_document_type_id': self.env.ref('l10n_pe.document_type01').id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_id': self.env.ref('uom.product_uom_kgm').id,
                'price_unit': 2000.0,
                'quantity': 5,
                'price_subtotal':90
            })],
        })
        
        self.payment = self.env['account.payment'].create({
            'partner_id': self.partner.id,
            'amount': 100.0,
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'journal_id': self.journal.id,
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
            'reference_invoice': self.invoice.id,
            'detractions_constancy_number': '1234567890'
        })

        
    def test_account_action_payment(self):
        product_without_detraction = self.env['product.product'].create({
            'name': 'Product without Detraction',
            'l10n_pe_withhold_percentage': 0.0
        })

        invoice_no_detraction = self.env['account.move'].create({
            'partner_id': self.partner.id,
            'move_type': 'out_invoice',
            'currency_id': self.env.ref('base.PEN').id,
            'invoice_line_ids': [(0, 0, {
                'product_id': product_without_detraction.id,
                'quantity': 1,
                'price_unit': 100.0
            })]
        })

        self.payment.reference_invoice = invoice_no_detraction

        self.payment.calculate_detractions()
        self.assertEqual(self.payment.amount, invoice_no_detraction.invoice_line_ids.price_unit)
        self.assertTrue(self.payment.currency_id)
        self.assertTrue(self.payment.destination_account_id)
        
    
    def test_calculate_detractions_in_pen(self):
        self.payment.calculate_detractions()
        expected_amount = round(self.invoice.amount_total * (10.0 / 100))
        self.assertEqual(self.payment.amount, 100)

        self.assertEqual(self.payment.currency_id, self.invoice.currency_id)
