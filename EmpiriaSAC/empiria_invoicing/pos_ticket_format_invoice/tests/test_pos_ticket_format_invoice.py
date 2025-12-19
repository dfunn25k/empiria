# -*- coding: utf-8 -*-
from odoo.tests import common
from odoo.tests.common import Form
from odoo.exceptions import UserError

class TestPosTicketFormatInvoice(common.TransactionCase):

    def setUp(self):
        super(TestPosTicketFormatInvoice, self).setUp()
        self.journal_model = self.env['account.journal']
        self.move_model = self.env['account.move']
        self.partner_model = self.env['res.partner']
        self.product_model = self.env['product.product']

    def test_01_account_journal_address_point_emission(self):
        """Test the new field 'address_point_emission' in account.journal"""
        journal = self.journal_model.create({
            'name': 'Test Journal',
            'type': 'sale',
            'code': 'TST',
            'address_point_emission': 'Test Address'
        })
        self.assertEqual(journal.address_point_emission, 'Test Address', 
                         "The address_point_emission field is not set correctly")
        print('--------TEST - Verificacion Account Journal Address point emission OK-------')

    def test_02_invoice_report_paperformat(self):
        """Test the existence of the new paperformat for invoice tickets"""
        paperformat = self.env.ref('pos_ticket_format_invoice.paperformat_print_invoice_ticket', raise_if_not_found=False)
        self.assertTrue(paperformat, "Paperformat for invoice tickets not found")
        self.assertEqual(paperformat.name, 'Invoice Ticket', 
                         "Paperformat name is not correct")
        print('--------TEST - Verificacion Invoice Report Paperformat OK-------')

    def test_03_invoice_report_action(self):
        """Test the existence of the new report action for invoice tickets"""
        report_action = self.env.ref('pos_ticket_format_invoice.account_invoices_tickets', raise_if_not_found=False)
        self.assertTrue(report_action, "Report action for invoice tickets not found")
        self.assertEqual(report_action.name, 'Facturas Ticket', 
                         "Report action name is not correct")
        print('--------TEST - Verificacion Invoice Report Action OK-------')

    def test_04_invoice_report_template(self):
        """Test the invoice report template rendering"""
        partner = self.partner_model.create({
            'name': 'Test Partner',
            'vat': '123456789',
        })
        product = self.product_model.create({
            'name': 'Test Product',
            'type': 'consu',
            'list_price': 100,
        })
        invoice_form = Form(self.move_model.with_context(default_move_type='out_invoice'))
        invoice_form.partner_id = partner
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = product
            line_form.quantity = 1
        invoice = invoice_form.save()
        invoice.action_post()
        
        report_action = self.env.ref('pos_ticket_format_invoice.account_invoices_tickets', raise_if_not_found=False)
        self.assertTrue(report_action, "Report action not found")
        
        try:
            report_result = report_action.report_action(invoice)
            self.assertTrue(report_result, "Report action did not return a result")
            self.assertIn(report_result['type'], ['ir.actions.report', 'ir.actions.act_window'], 
                          f"Unexpected action type returned: {report_result['type']}")
            
            if report_result['type'] == 'ir.actions.act_window':
                self.assertIn('view_mode', report_result, "Window action is missing view_mode")
            elif report_result['type'] == 'ir.actions.report':
                self.assertIn('report_type', report_result, "Report action is missing report_type")
            
        except UserError as e:
            self.fail(f"Generacion de reporte Fallida: {str(e)}")
        print('--------TEST - Verificacion Invoice Report Template OK-------')

    def test_05_invoice_amount_to_text(self):
        """Test the _amount_to_text method"""
        partner = self.partner_model.create({
            'name': 'Test Partner',
            'vat': '123456789',
        })
        product = self.product_model.create({
            'name': 'Test Product',
            'type': 'consu',
            'list_price': 100,
        })
        invoice_form = Form(self.move_model.with_context(default_move_type='out_invoice'))
        invoice_form.partner_id = partner
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = product
            line_form.quantity = 1
        invoice = invoice_form.save()
        
        amount_text = invoice._amount_to_text()
        self.assertTrue(amount_text, "Amount to text conversion failed")
        self.assertIsInstance(amount_text, str, "Amount to text should return a string")
        print('--------TEST - Verificacion Invoice Amount to Text OK-------')






        




