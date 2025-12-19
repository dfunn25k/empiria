from odoo.tests.common import TransactionCase
from odoo.exceptions import MissingError

class TestStockPicking(TransactionCase):
        
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        user_admin = self.env.ref("base.user_admin")
        self.env = self.env(user=user_admin)
        self.ts_stock_picking = self.env['stock.picking'].create({
            "name": "exampleNamePicking",
            "picking_type_id": 2,
            "location_id": 2,
            "location_dest_id": 3,
            "sunat_sequence":False,
            "l10n_pe_edi_reason_for_transfer":"01",
            "state":"draft"    
        })
        self.ts_partner = self.env['res.partner'].create({
            'name': 'TestExapple',
            'email': 'test_partner@example.com'
        })
        self.ts_location = self.env['stock.location'].create({
            'name':'ExampleName',
            'direction_id': self.ts_partner.id
        })
           
    def test_fields_values_ts_stock_picking(self):
        self.assertEqual(self.ts_stock_picking.name, "exampleNamePicking")
        self.assertEqual(self.ts_stock_picking.picking_type_id.id, 2)
        self.assertEqual(self.ts_stock_picking.location_id.id, 2)
        self.assertEqual(self.ts_stock_picking.location_dest_id.id, 3)
        self.assertFalse(self.ts_stock_picking.sunat_sequence)
        self.assertEqual(self.ts_stock_picking.l10n_pe_edi_reason_for_transfer, "01")
        self.assertEqual(self.ts_stock_picking.state, "draft")
        
        print("--------------------TEST FIELDS OK--------------------")
        
    def test_get_prefix(self):
        prefix = self.ts_stock_picking.get_prefix()
        self.assertEqual(prefix, [('TP01-', 'TP01-')])
        
        print("--------------------TEST get_prefix OK--------------------")

    def test_l10n_pe_edi_get_delivery_guide_values(self):
        values = self.ts_stock_picking._l10n_pe_edi_get_delivery_guide_values()
        sample_stock_picking = self.env['stock.picking'].browse(1) 
        sample_uom_uom = self.env['uom.uom'].browse(2) 
        sample_res_partner = self.env['res.partner'].browse(3) 
        
        self.assertEqual(values['date_issue'], '2023-11-09')
        self.assertEqual(values['time_issue'], '00:00:00')
        self.assertEqual(values['l10n_pe_edi_observation'], 'Guía')
        self.assertIsInstance(values['record'], sample_stock_picking.__class__)
        self.assertIsInstance(values['weight_uom'], sample_uom_uom.__class__)
        self.assertIsInstance(values['warehouse_address'], sample_res_partner.__class__)

        print("------TEST _l10n_pe_edi_get_delivery_guide_values OK------")
    
    def test_l10n_pe_edi_request_token_key_error(self):
        self.credentials = self.ts_stock_picking._l10n_pe_edi_get_sunat_guia_credentials()
        if 'access_id' in self.credentials:
            try:         
                result = self.ts_stock_picking._l10n_pe_edi_request_token(self.credentials)      
                assert result is not None  
            except Exception as e:       
                self.fail(f"Se produjo un error: {str(e)}")
        else:
            self.skipTest("access_id no presente en las credenciales")
        
        