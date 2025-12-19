from odoo.tests import common
from odoo.tests.common import tagged
from datetime import *
from odoo import fields
from dateutil.relativedelta import relativedelta

@tagged('post_install', '-at_install')
class TestRestrictionMoveOrigin(common.TransactionCase):
    def setUp(self):
        super().setUp()
        
        self.account = self.env['account.account'].create({
            'code':'33611.0111',
            'name':'Equipo procesamiento de info',
            'account_type':'asset_fixed',
            'create_asset':'draft'
        })
        self.account_depreciation = self.env['account.account'].search([('account_type','=','asset_current')])[0]
        self.account_expense = self.env['account.account'].search([('account_type','=','expense')])[0]
        
        self.asset = self.env['account.asset'].create({
            'name':'Equipos Informaticos',
            'method':'linear',
            'method_number':60,
            'method_period':'1',
            'account_asset_id':self.account.id,
            'account_depreciation_id': self.account_depreciation.id,
            'account_depreciation_expense_id': self.account_expense.id
        })
        
        self.product = self.env['product.product'].create({
            'name': 'producto test',
            'uom_po_id': self.env.ref('uom.product_uom_kgm').id,
            'uom_id': self.env.ref('uom.product_uom_kgm').id,
            'lst_price': 1000.0,
        })
        self.tax_group = self.env['account.tax.group'].create({
            'name': "IGV",
            'l10n_pe_edi_code': "IGV",
        })

        self.tax_18 = self.env['account.tax'].create({
            'name': 'tax_18',
            'amount_type': 'percent',
            'amount': 18,
            'l10n_pe_edi_tax_code': '1000',
            'l10n_pe_edi_unece_category': 'S',
            'type_tax_use': 'sale',
            'tax_group_id': self.tax_group.id,
        })
        
        self.invoice = self.env['account.move'].create({
            'name':'Factura cliente',
            'invoice_date':date.today(),
            'journal_id':self.env['account.journal'].search([('type','=','purchase')])[0].id,
            'currency_id': self.env['res.currency'].search([('name','=','PEN')])[0].id,
            'l10n_latam_document_type_id': self.env.ref('l10n_pe.document_type01').id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_id': self.env.ref('uom.product_uom_kgm').id,
                'price_unit': 2000.0,
                'quantity': 5,
                'tax_ids': [(6, 0, self.tax_18.ids)],
            })],
        })
        
        self.move_line = self.env['account.move.line'].create({
            'name': 'Depreciation Line',
            'debit': 200,
            'credit': 0,
            'account_id': self.account.id,
            'move_id': self.invoice.id,
        })
        
    
    def test_move_origin(self): 
        self.assertTrue(self.asset)
        
        self.assertEqual(self.asset.name, 'Equipos Informaticos')
        self.assertEqual(self.asset.method, 'linear')
        self.assertEqual(self.asset.method_number, 60)
        self.assertEqual(self.asset.method_period, '1')
        self.assertEqual(self.asset.account_asset_id.id, self.account.id)
        self.assertEqual(self.asset.account_depreciation_id.id, self.account_depreciation.id)
        self.assertEqual(self.asset.account_depreciation_expense_id.id, self.account_expense.id)
        
        draft_moves = self.asset.depreciation_move_ids.filtered(lambda mv: mv.state == 'draft')
        if draft_moves:
            self.asserTrue(draft_moves)
            
        self.asset.state = 'open'
        self.asset.compute_depreciation_board()

        draft_moves = self.asset.depreciation_move_ids.filtered(lambda mv: mv.state == 'draft')
        self.assertEqual(len(draft_moves), 0)

        new_moves = self.env['account.move'].search([('asset_id', '=', self.asset.id)])
        posted_moves = new_moves.filtered(lambda mv: mv.state == 'posted')
        
        rate = self.asset._get_to_force_exchange_rate()
        expected_rate = 1.0
        self.assertEqual(rate, expected_rate)
        
        if posted_moves:
            self.assertTrue(posted_moves)
    
    def test_move_value(self):
        
        self.assertTrue(self.account)
        self.assertEqual(self.account.code, '33611.0111')
        self.assertEqual(self.account.name, 'Equipo procesamiento de info')
        self.assertEqual(self.account.account_type, 'asset_fixed')
        self.assertEqual(self.account.create_asset, 'draft')
    
        depreciation = self.invoice._get_depreciation()
        
        expected_depreciation = (self.asset.original_value - self.asset.salvage_value - self.move_line.debit)
        self.assertTrue(expected_depreciation)
        self.assertFalse(depreciation)
        
        self.invoice._compute_depreciation_value()
        self.assertEqual(self.invoice.depreciation_value, 0.0)
        
        assets = self.invoice._auto_create_asset()

        for asset in assets:
            self.assertEqual(asset.name, 'Depreciation Line')
            self.assertEqual(asset.company_id, self.invoice.company_id)
            self.assertEqual(asset.currency_id, self.invoice.currency_id)
            self.assertEqual(asset.original_value, self.move_line.price_total)
            self.assertEqual(asset.state, 'draft')
            self.assertEqual(asset.original_move_line_ids.mapped('id'), [self.move_line.id])
            
            message = ('%s created from invoice') % ('Asset')
            self.assertTrue(any(msg.body.startswith(message) for msg in asset.message_ids))
        
 
       
