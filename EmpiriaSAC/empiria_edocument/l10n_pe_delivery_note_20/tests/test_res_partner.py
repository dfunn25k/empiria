from odoo.tests.common import TransactionCase

class TestResPartner(TransactionCase):
        
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        user_admin = self.env.ref("base.user_admin")
        self.env = self.env(user=user_admin)
        self.ts_res_partner = self.env['res.partner'].create({
            'name': 'ExamplePartner',
            'email': 'example_partner@example.com'
        })
        self.ts_res_config = self.env['res.config.settings'].create({
            'l10n_pe_edi_delivery_test_env':False
        })
        self.ts_res_company = self.env['res.company'].create({
            'name' : 'ExampleResCompany',
            'l10n_pe_edi_delivery_test_env':False
        })
        
          
    def test_l10n_pe_edi_delivery_test_env(self):
        self.assertFalse(self.ts_res_company.l10n_pe_edi_delivery_test_env)
        print("--------TEST l10n_pe_edi_delivery_test_env OK---------------")
    
    def test_get_structured_address(self):
    
        structured_address = self.ts_res_partner.get_structured_address()
        self.assertNotEqual(structured_address, "")
        print("--------TEST get_structured_address OK---------------")

    def test_get_address_format_report(self):
      
        address_format_report = self.ts_res_partner.get_address_format_report()
        self.assertNotEqual(address_format_report, "")
        print("---------TEST get_address_format_report OK--------------")
    
    def test_onchange_l10n_pe_edi_delivery_test_env(self):
        self.assertEqual(self.ts_res_config._onchange_l10n_pe_edi_delivery_test_env(),None)
        print("---------TEST _onchange_l10n_pe_edi_delivery_test_env OK--------------")
        
        
    
    