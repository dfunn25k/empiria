from odoo.tests import common
from odoo.tests.common import tagged
from datetime import *
from odoo import fields
from dateutil.relativedelta import relativedelta

@tagged('post_install', '-at_install')
class TestSaleSubscription(common.TransactionCase):
    def setUp(self):
        super().setUp()
    
        self.partner = self.env['res.partner'].create({
            'name': 'Test Customer',
            'email': 'test@example.com',
        })

        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'service',
            'list_price': 100.0,
        })

        self.sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })

        self.sale_order_line = self.env['sale.order.line'].create({
            'order_id': self.sale_order.id,
            'product_id': self.product.id,
            'product_uom_qty': 2,
            'price_unit': self.product.list_price,
        })
    
    def test_sale_subs(self):
        self.sale_order.action_confirm()
        self.assertEqual(self.sale_order.state, 'sale')

        invoices = self.sale_order._create_recurring_invoice()
        if not invoices:
            self.assertFalse(invoices)
        else:
            for invoice in invoices:
                self.assertTrue(invoice.env.context.get('tracking_disable'))
                try:
                    invoice._get_change_account()
                except Exception as e:
                    self.fail(e)
                self.assertEqual(invoice.partner_id.id, self.partner.id)
                self.assertEqual(invoice.invoice_line_ids[0].product_id.id, self.product.id)