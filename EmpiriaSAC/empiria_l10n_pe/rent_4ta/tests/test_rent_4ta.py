from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import datetime
import json

class TestRent4taFiles(TransactionCase):

    def setUp(self):
        super(TestRent4taFiles, self).setUp()

        self.company = self.env['res.company'].create({'name': 'Test Company'})

        self.journal = self.env['account.journal'].create({
            'name': 'Sales Journal',
            'type': 'sale',
            'code': 'SAJ',
            'company_id': self.company.id,
        })

        self.rent4ta_file = self.env['rent.4ta.files'].create({
            'date_from': '2024-01-01',
            'date_to': '2024-03-31',
            'company_id': self.company.id,
        })
        print("<<<< SET UP >>>>>")

    def test_name_get(self):
        name = self.rent4ta_file.name_get()
        expected_name = "%s - %s" % (self.rent4ta_file.date_from, self.rent4ta_file.date_to)
        self.assertEqual(name[0][1], expected_name)
        print("<<<< TEST NAME >>>>>")

    def test_action_generate_files(self):
        partner = self.env['res.partner'].create({'name': 'Test Partner', 'vat': '12345678901'})
        l10n_latam_document_type = self.env['l10n_latam.document.type'].create({
            'name': 'Factura',
            'code': '02',
            'internal_type': 'invoice',
            'country_id': self.env.ref('base.pe').id,
        })

        journal = self.env['account.journal'].search([('type', '=', 'sale'), ('company_id', '=', self.company.id)], limit=1)

        self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'l10n_latam_document_type_id': l10n_latam_document_type.id,
            'state': 'draft',
            'company_id': self.company.id,
            'journal_id': journal.id,  
            'invoice_date': '2024-01-15',
            'invoice_payments_widget': json.dumps({
                'content': [{'date': '2024-01-20'}]
            })
        })

        self.rent4ta_file.action_generate_files()

        self.assertIsNotNone(self.rent4ta_file.ps4_binary, "El archivo ps4 debería generarse")
        self.assertIsNotNone(self.rent4ta_file.quarter_binary, "El archivo 4ta debería generarse")

        print("<<<< TEST GENERATE >>>>>")

    def test_generate_data_report_rent_4ta(self):

        data_ps4, data_4ta = self.rent4ta_file.generate_data_report_rent_4ta()
        self.assertIsInstance(data_ps4, dict, "El resultado debería ser un diccionario para PS4")
        self.assertIsInstance(data_4ta, list, "El resultado debería ser una lista para 4ta")
        print("<<<< TEST GENERATE REPORT >>>>>")