import unittest
from odoo.tests import TransactionCase
from odoo.tests.common import Form
from odoo import fields
from dateutil.relativedelta import relativedelta

class TestCustomPaymentTermModule(TransactionCase):

    def setUp(self):
        super(TestCustomPaymentTermModule, self).setUp()
        self.payment_term_model = self.env['account.payment.term']
        self.payment_term_line_model = self.env['account.payment.term.line']
        self.move_model = self.env['account.move']
        self.partner = self.env['res.partner'].create({'name': 'Test Partner'})
        self.product = self.env['product.product'].create({'name': 'Test Product'})

    def test_compute_needed_terms(self):
        # Test the modified _compute_needed_terms method
        invoice = self.move_model.create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'price_unit': 100,
            })],
        })
        invoice._compute_needed_terms()
        self.assertTrue(invoice.needed_terms)
        term_key = list(invoice.needed_terms.keys())[0]
        self.assertIn('tmp_date_maturity', term_key)
        print('-------------------TEST PAYMENT TERM LINES PART-1 OK -------------------')

    def test_compute_term_key(self):
        # Test the modified _compute_term_key method
        invoice = self.move_model.create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'price_unit': 100,
            })],
        })
        invoice._compute_needed_terms()
        payment_term_line = invoice.line_ids.filtered(lambda l: l.display_type == 'payment_term')[0]
        payment_term_line._compute_term_key()
        self.assertTrue(payment_term_line.term_key)
        self.assertIn('tmp_date_maturity', payment_term_line.term_key)
        print('-------------------TEST PAYMENT TERM LINES PART-2 OK -------------------')
    
    def test_compute_terms(self):
        # Test the modified _compute_terms method
        payment_term = self.payment_term_model.create({
            'name': 'Test Payment Term',
            'line_ids': [(0, 0, {
                'value': 'balance',
                'l10n_pe_is_detraction_retention': True,
            })]
        })
        date_ref = fields.Date.today()
        company = self.env.company
        currency = company.currency_id
        result = payment_term._compute_terms(
            date_ref, currency, company, 100, 100, 1, 1000, 1000
        )
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]['l10n_pe_is_detraction_retention'])
        print('-------------------TEST PAYMENT TERM LINES PART-3 OK -------------------')
    
    def test_get_amount_by_date(self):
        # Test the modified _get_amount_by_date method
        payment_term = self.payment_term_model.create({
            'name': 'Test Payment Term',
            'line_ids': [(0, 0, {
                'value': 'balance',
                'l10n_pe_is_detraction_retention': True,
            })]
        })
        date_ref = fields.Date.today()
        terms = payment_term._compute_terms(
            date_ref, self.env.company.currency_id, self.env.company, 100, 100, 1, 1000, 1000
        )
        result = payment_term._get_amount_by_date(terms, self.env.company.currency_id)
        self.assertEqual(len(result), 1)
        self.assertIn('tmp_date_maturity', list(result.values())[0])
        print('-------------------TEST PAYMENT TERM LINES PART-4 OK -------------------')
    
    def test_get_data_from_line_ids(self):

        payment_term = self.payment_term_model.create({
            'name': 'Test Payment Term with Detraction',
            'line_ids': [(0, 0, {
                'value': 'balance',
                'l10n_pe_is_detraction_retention': True,
            })]
        })
        # Test the new method _get_data_from_line_ids
        payment_term_line = self.payment_term_line_model.create({
            'value': 'balance',
            'payment_id': payment_term.id,
            'l10n_pe_is_detraction_retention': True,
        })
        date_ref = fields.Date.today()
        result = payment_term_line._get_data_from_line_ids(date_ref)
        self.assertEqual(result['date'], date_ref)
        self.assertTrue(result['l10n_pe_is_detraction_retention'])
        print('-------------------TEST PAYMENT TERM LINES PART-5 OK -------------------')

    def test_invoice_with_detraction_retention(self):
        # Test creating an invoice with a payment term that has detraction/retention
        payment_term = self.payment_term_model.create({
            'name': 'Test Payment Term with Detraction',
            'line_ids': [(0, 0, {
                'value': 'balance',
                'l10n_pe_is_detraction_retention': True,
            })]
        })
        invoice_form = Form(self.move_model.with_context(default_move_type='out_invoice'))
        invoice_form.partner_id = self.partner
        invoice_form.invoice_payment_term_id = payment_term
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product
            line_form.quantity = 1
            line_form.price_unit = 100
        invoice = invoice_form.save()
        invoice._compute_needed_terms()
        
        payment_term_line = invoice.line_ids.filtered(lambda l: l.display_type == 'payment_term')[0]
        self.assertTrue(payment_term_line.l10n_pe_is_detraction_retention)
        print('-------------------TEST PAYMENT TERM LINES PART-6 OK -------------------')

    def test_payment_term_line_detraction_retention(self):
        # Test the new field l10n_pe_is_detraction_retention
        payment_term = self.payment_term_model.create({
            'name': 'Test Payment Term',
            'line_ids': [(0, 0, {
                'value': 'balance',
                'l10n_pe_is_detraction_retention': True,
            })]
        })
        self.assertTrue(payment_term.line_ids[0].l10n_pe_is_detraction_retention)
        print('-------------------TEST PAYMENT TERM LINES PART-7 OK -------------------')
