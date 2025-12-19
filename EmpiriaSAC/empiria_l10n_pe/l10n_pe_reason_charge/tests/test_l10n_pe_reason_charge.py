from odoo.tests.common import TransactionCase

class TestL10nPeReasonCharge(TransactionCase):

    def setUp(self):
        super(TestL10nPeReasonCharge, self).setUp()

        self.product_tmpl_with_advance = self.env['product.template'].create({
            'name': 'Product with advance',
            'l10n_pe_advance': True,
        })
        self.product_tmpl_without_advance = self.env['product.template'].create({
            'name': 'Product without advance',
            'l10n_pe_advance': False,
        })
        self.product_with_advance = self.env['product.product'].create({
            'product_tmpl_id': self.product_tmpl_with_advance.id,
        })
        self.product_without_advance = self.env['product.product'].create({
            'product_tmpl_id': self.product_tmpl_without_advance.id,
        })
        self.invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.env.ref('base.res_partner_1').id,
        })
        self.edi_format = self.env['account.edi.format'].create({
            'name': 'Test Format',
            'code': 'test_code' 
        })

    def test_compute_exist_advance(self):
        """Prueba para verificar el campo compute exist_advance"""
        # Agregar línea de factura sin advance
        self.invoice.write({
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product_without_advance.id,
                'quantity': 1,
                'price_unit': 100.0
            })]
        })
        self.invoice._compute_exist_advance()
        self.assertFalse(self.invoice.exist_advance)

        # Agregar línea de factura con advance
        self.invoice.write({
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product_with_advance.id,
                'quantity': 1,
                'price_unit': 100.0
            })]
        })
        self.invoice._compute_exist_advance()
        self.assertTrue(self.invoice.exist_advance)
        
        print('--------------------TEST EXIST ADVANCE OK--------------------')

    def test_carrier_reference_update_template_base(self):
        """Prueba para verificar la actualización de la plantilla XML en AccountEdiFormat"""
        self.edi_format.carrier_reference_update_template_base()
        template = self.env.ref('l10n_pe_edi.pe_ubl_2_1_common')
        # print(template.arch_base)
        self.assertIn('<cbc:ID', template.arch_base)
        print('--------------------TEST UPDATE TEMPLATE OK--------------------')
