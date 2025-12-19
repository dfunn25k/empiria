from odoo.tests.common import TransactionCase
from odoo import fields

class TestAccountValueUnit(TransactionCase):

    def setUp(self):
        super(TestAccountValueUnit, self).setUp()
        
        self.tax_18 = self.env['account.tax'].create({
            'name': 'Tax 18%',
            'amount': 18.0,
            'type_tax_use': 'sale',
        })
        self.tax_10 = self.env['account.tax'].create({
            'name': 'Tax 10%',
            'amount': 10.0,
            'type_tax_use': 'sale',
        })

        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'list_price': 2500.0,
        })
        print("-----<<<<<< SET UP >>>>>>-----")

    def test_account_value_unit_with_18_percent_tax(self):
        
        move = self.env['account.move'].create({
            'name': 'Test Move',
            'move_type': 'out_invoice',  
            'journal_id': self.env['account.journal'].search([], limit=1).id,  
            'date': fields.Date.today(),
        })

        move_line = self.env['account.move.line'].create({
            'move_id': move.id,  
            'product_id': self.product.id,
            'price_unit': 2500.0,
            'quantity': 1,
            'tax_ids': [(6, 0, [self.tax_18.id])],
        })

        self.assertAlmostEqual(move_line.account_value_unit, round(2500.0 / 1.18 , 2))

        print("-----<<<<<< TEST 18 percent >>>>>>-----")
