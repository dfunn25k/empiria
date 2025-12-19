import logging
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)

class TestDocumentInSupplierInvoice(TransactionCase):

    def setUp(self):
        super(TestDocumentInSupplierInvoice, self).setUp()
        # Creación de producto
        self.product = self.env['product.product'].create({
            'name': 'Product',
            'standard_price': 600.0,
            'list_price': 147.0,
            'detailed_type': 'consu',
        })
        # Creación del partner en Perú
        self.partner_pe = self.env['res.partner'].create({
            'name': "Partner PE",
            'country_id': self.env.ref('base.pe').id,
        })

    def test_create_out_invoice(self):
        # Crear un nuevo diario
        journal = self.env['account.journal'].create({
            'name': 'Test Journal',
            'code': 'TESTINV',
            'type': 'sale',
            'company_id': self.env.company.id,
            'l10n_latam_use_documents': False,
        })
        
        l10n_latam_document_type = self.env['l10n_latam.document.type'].search([
            ('code', '=', '03'),
            ('country_id.code', '=', 'PE')
        ])
        l10n_latam_document_type.account_journal_id_sale = journal.id
        
        # Crear una factura de venta (out_invoice)
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'date': '2024-01-01',
            'partner_id': self.partner_pe.id,
            'journal_id': journal.id,
            'l10n_latam_document_type_id': l10n_latam_document_type.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'price_unit': 100.0,
                'tax_ids': [],
            })]
        })

        self.assertTrue(invoice, "No se pudo crear la factura de venta.")
        self.assertEqual(invoice.move_type, 'out_invoice', "El tipo de movimiento no es 'out_invoice'.")
        self.assertEqual(invoice.partner_id, self.partner_pe, "El socio comercial no es el esperado.")
        self.assertEqual(invoice.journal_id, journal, "El diario no es el esperado.")

    def test_create_in_invoice(self):
        # Buscar el diario
        journal = self.env['account.journal'].search([
            ('code', '=', 'BILL')
        ])
        if not journal:
            journal = self.env['account.journal'].search([
                ('code', '=', 'FACTU')
            ])
        l10n_latam_document_type = self.env['l10n_latam.document.type'].search([
            ('code', '=', '01'),
            ('country_id.code', '=', 'PE')
        ])
        # Deshabilitar el uso de documentos LATAM en el diario
        journal.l10n_latam_use_documents = False
        l10n_latam_document_type.account_journal_id = journal.id
        
        # Crear una factura de compra (in_invoice)
        invoice = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'date': '2024-01-02',
            'partner_id': self.partner_pe.id,
            'journal_id': journal.id,
            'l10n_latam_document_type_id': l10n_latam_document_type.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'price_unit': 100.0,
                'tax_ids': []
            })]
        })
        
        self.assertTrue(invoice, "No se pudo crear la factura de compra.")
        self.assertEqual(invoice.move_type, 'in_invoice', "El tipo de movimiento no es 'in_invoice'.")
        self.assertEqual(invoice.partner_id, self.partner_pe, "El socio comercial no es el esperado.")
        self.assertEqual(invoice.journal_id, journal, "El diario no es el esperado.")