from odoo.tests import common
from odoo.tests.common import tagged
from datetime import date

@tagged('post_install', '-at_install')
class TestAccountDiscountGlobal(common.TransactionCase):

    def setUp(self):
        super().setUp()
        
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'vat': '123456'
        })
        
        self.product = self.env['product.product'].create({
            'name': 'Producto Test',
            'uom_po_id': self.env.ref('uom.product_uom_kgm').id,
            'uom_id': self.env.ref('uom.product_uom_kgm').id,
            'lst_price': 1000.0,
            'global_discount': True,  # Configura el descuento global aquí
        })
        
        self.tax_group = self.env['account.tax.group'].create({
            'name': "IGV",
            'l10n_pe_edi_code': "IGV",
        })
        
        self.tax_18 = self.env['account.tax'].create({
            'name': 'Tax 18%',
            'amount_type': 'percent',
            'amount': 18,
            'l10n_pe_edi_tax_code': '1000',
            'l10n_pe_edi_unece_category': 'S',
            'type_tax_use': 'sale',
            'tax_group_id': self.tax_group.id,
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
                'tax_ids': [(6, 0, self.tax_18.ids)],
                'price_subtotal':90
            })],
        })

    def test_discount_global(self):
        self.invoice.action_post()
        for move in self.invoice:
            price_subtotal_with_discount = 0.0
            price_subtotal_without_discount = 0.0

            for line in move.invoice_line_ids:
                if move.is_invoice(True):
                    if line.product_id.global_discount and line.price_subtotal < 0:
                        price_subtotal_with_discount += line.price_subtotal

                    if not line.product_id.global_discount:
                        price_subtotal_without_discount += line.price_subtotal

            move.discount_percent_global = abs(price_subtotal_with_discount / max(price_subtotal_without_discount, 1) * 100)
            
            discount = move.discount_percent_global if line.price_subtotal < 0 else 0.00
            self.assertEqual(move.discount_percent_global,0.00)
    
    def test_fields_discount_global(self):
        self.invoice.action_post()
        
        self.assertEqual(self.invoice.partner_id, self.partner)
        self.assertEqual(self.invoice.journal_id.type, 'sale')
        self.assertEqual(self.invoice.currency_id.name, 'PEN')
        self.assertEqual(self.invoice.invoice_date, date.today())
        self.assertEqual(self.invoice.state, 'posted' )
        
        self.assertEqual(len(self.invoice.invoice_line_ids), 1)
        invoice_line = self.invoice.invoice_line_ids[0]
        self.assertEqual(invoice_line.product_id, self.product)
        self.assertEqual(invoice_line.product_uom_id, self.env.ref('uom.product_uom_kgm'))
        self.assertEqual(invoice_line.price_unit, 2000.0)
        self.assertEqual(invoice_line.quantity, 5)
        
        self.assertEqual(invoice_line.tax_ids, self.tax_18)



        
        
        
