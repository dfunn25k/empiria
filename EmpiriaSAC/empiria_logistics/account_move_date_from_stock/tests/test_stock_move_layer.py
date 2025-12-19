from odoo.tests import common
from odoo.tests.common import tagged
from odoo import fields
from datetime import *

@tagged('post_install', '-at_install')
class TestStockMoveLayer(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.journal = self.env['account.journal'].search([('code', '=', 'STJ'), ('company_id', '=', self.env.company.id)], limit=1)
        if not self.journal:
            self.journal = self.env['account.journal'].create({
                'name': 'Stock Journal',
                'type': 'general',
                'code': 'STJ',
            })

        self.debit_account = self.env['account.account'].create({
            'name': 'Debit Account',
            'code': '400001',
            'company_id': self.env.company.id,
        })

        self.credit_account = self.env['account.account'].create({
            'name': 'Credit Account',
            'code': '400002',
            'company_id': self.env.company.id,
        })

        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'product',
            'categ_id': self.env.ref('product.product_category_all').id,
        })

        self.stock_move = self.env['stock.move'].create({
            'name': 'Test Stock Move',
            'product_id': self.product.id,
            'product_uom_qty': 10,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
        })

        self.stock_valuation_layer = self.env['stock.valuation.layer'].create({
            'product_id': self.product.id,
            'quantity': 10,
            'unit_cost': 10,
            'value': 100,
            'stock_move_id': self.stock_move.id,
            'company_id': self.env.company.id,
        })
    def test_create_stock_valuation_layer_with_stock_move(self):
        valuation_layer = self.env['stock.valuation.layer'].create([{
            'stock_move_id': self.stock_move.id,
            'product_id': self.stock_move.product_id.id,
            'quantity': 1,
            'unit_cost': 100.0,
            'value': 100.0,
            'company_id': self.env.company.id,
        }])

        self.assertEqual(valuation_layer.accounting_date, self.stock_move.date)

    def test_prepare_account_move_vals(self):
        qty = 5
        cost = 100.0
        description = "Test Stock Valuation"
        svl_id = self.stock_valuation_layer.id  
        journal_id = self.journal.id
        credit_account_id = self.credit_account.id
        debit_account_id = self.debit_account.id

        move_vals = self.stock_move._prepare_account_move_vals(
            credit_account_id=credit_account_id,
            debit_account_id=debit_account_id,
            journal_id=journal_id,
            qty=qty,
            description=description,
            svl_id=svl_id,
            cost=cost
        )
     
        self.assertEqual(move_vals['journal_id'], journal_id)
        self.assertEqual(move_vals['ref'], description)
        self.assertEqual(move_vals['stock_move_id'], self.stock_move.id)
        self.assertEqual(move_vals['move_type'], 'entry')
        self.assertEqual(move_vals['date'], fields.Date.context_today(self.stock_move))  
