from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, RedirectWarning

class TestAccountMove(TransactionCase):

    def setUp(self):
        super(TestAccountMove, self).setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'is_company': True,
        })
        self.document_type = self.env['l10n_latam.document.type'].create({
            'name': 'Test Document Type',
            'code': '01',
            'country_id': self.env.ref('base.pe').id,
            'prefix_long': 4,
            'prefix_length_validation': 'equal',
            'prefix_validation': 'numbers',
            'correlative_long': 8,
            'correlative_length_validation': 'equal',
            'correlative_validation': 'numbers',
        })
        self.currency_pen = self.env['res.currency'].search([('name', '=', 'PEN')], limit=1)
        self.journal = self.env['account.journal'].create({
            'name': 'Test Journal',
            'type': 'sale',
            'code': 'TEST',
        })
        print("---------- SET UP ------------")
    
    def test_error_dialog_validation(self):
        invoice = self.env['account.move'].create({
            'partner_id': self.partner.id,
            'move_type': 'out_invoice',
            'ref': 'F001-12345678',
            'l10n_latam_document_type_id': self.document_type.id,
            'currency_id': self.currency_pen.id,
            'journal_id': self.journal.id,
            'currency_id': 66,
        })

        invoice._compute_error_dialog()
        if invoice.error_dialog == False:
            r = ''
            self.assertEqual(r, '', "La validación esta vacia.")
        else:
            self.assertEqual(invoice.error_dialog, '', "La validación debería pasar sin errores.")
        print("-----------------TEST------------------")

        

    