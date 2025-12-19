from odoo.tests.common import TransactionCase
import json

class TestAccountMove(TransactionCase):
    def setUp(self):
        super(TestAccountMove, self).setUp()

        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'email': 'testpartner@example.com',
            'phone': '+1234567890',
        })

        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'list_price': 10.0,
        })

        self.invoice = self.env['account.move'].create({
            'partner_id': self.partner.id,
            'invoice_date': '2023-03-30',
            'move_type': 'out_invoice',
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'name': 'Test Product',
                'price_unit': 10.0,
                'quantity': 1,
            })],
        })

    def test_compute_tax_totals_json(self):
        self.invoice._compute_tax_totals_json()

        # Verify that the tax_totals_json field has been set
        self.assertIsNotNone(self.invoice.tax_totals_json)

        # Verify that the allow_tax_edition value is set to False
        tax_totals = json.loads(self.invoice.tax_totals_json)
        self.assertFalse(tax_totals['allow_tax_edition'])

        # Verify that the tax totals are correct
        self.assertEqual(tax_totals['amount_total'], 10.0)
        self.assertEqual(tax_totals['amount_untaxed'], 8.47)
        self.assertEqual(tax_totals['subtotals'][0]['name'], 'Untaxed Amount')
        self.assertEqual(tax_totals['subtotals'][0]['amount'], 8.47)
        self.assertEqual(len(tax_totals['groups_by_subtotal']['Untaxed Amount']), 1)

        # Verify that editing the tax_totals_json field works
        tax_totals['groups_by_subtotal']['Untaxed Amount'][0]['tax_group_amount'] = 2.0
        self.invoice.tax_totals_json = json.dumps(tax_totals)
        self.assertEqual(self.invoice.amount_total, 10.0)