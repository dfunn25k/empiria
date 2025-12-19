from odoo.tests import TransactionCase, tagged

@tagged('post_install', '-at_install')
class TestStockPicking(TransactionCase):

    def setUp(self):
        super(TestStockPicking, self).setUp()
        self.company = self.env['res.company'].create({
            'name': 'Test Company',
        })
        self.env.user.company_id = self.company
        
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'country_id': self.env.ref('base.pe').id, 
            'company_id': self.company.id,
        })
        
        self.picking = self.env['stock.picking'].create({
            'partner_id': self.partner.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
        })

    def test_picking_number_copy(self):
        """Probar que el campo picking_number no se copia cuando se duplica el registro"""
        self.picking.picking_number = 'PN123'
        duplicated_picking = self.picking.copy()
        self.assertFalse(duplicated_picking.picking_number)
        print('------------------TEST PICKING NUMBER COPY----------------')


    def test_picking_number_visibility(self):
        """Probar que el campo picking_number se muestra correctamente en la vista del formulario"""
        view = self.env.ref('l10n_pe_delivery_note_ple.stock_picking_view_form_inherit_l10n_pe_delivery_note_ple')
        view_arch = view.arch_db 
        # Verificar que el campo 'picking_number' está presente en la vista heredada
        self.assertIn('picking_number', view_arch)
        print('------------------TEST PICKING NUMBER VISIBILITY----------------')
