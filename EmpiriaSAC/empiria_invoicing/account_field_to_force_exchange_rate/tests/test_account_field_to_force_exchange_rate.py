from odoo import fields
from odoo.tests import TransactionCase

class TestAccountMoveForceExchangeRate(TransactionCase):

    def setUp(self):
        super(TestAccountMoveForceExchangeRate, self).setUp()

        self.currency_pen = self.env['res.currency'].search([('name', '=', 'PEN')], limit=1)

        if not self.currency_pen:
            raise ValueError("La moneda PEN no existe en la base de datos.")

        self.company = self.env.user.company_id

        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
        })

        self.product_template = self.env['product.template'].create({
            'name': 'Test Product',
            'list_price': 100.0,
            'sale_line_warn': 'warning',  
        })

        self.product = self.env['product.product'].search([('product_tmpl_id', '=', self.product_template.id)], limit=1)

        self.invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'currency_id': self.currency_pen.id,
            'company_id': self.company.id,
            'invoice_date': fields.Date.today(),
            'to_force_exchange_rate': 1,  
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'price_unit': 100.0,
            })],
        })
        print("<<<<<<<<<<<< SET UP >>>>>>>>>>>>")

    def test_force_exchange_rate(self):
        self.invoice._compute_currency_rate()

        self.assertEqual(self.invoice.to_force_exchange_rate, 1)
        actual_rate = self.invoice._get_actual_currency_rate()
        self.assertAlmostEqual(actual_rate, 1 / 1, places=6)
        print("<<<<<<<<<<<< TEST FORCE EXCHANGE RATE >>>>>>>>>>>>")
