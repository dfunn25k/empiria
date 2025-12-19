from odoo.tests.common import TransactionCase


class TestPosValidationByDocument(TransactionCase):

    def setUp(self):
        super(TestPosValidationByDocument, self).setUp()
        self.pos_config = self.env['pos.config'].create({
            'name': 'Test POS',
            'identify_client': 10.0, 
        })
        self.pos_session = self.env['pos.session'].create({
            'config_id': self.pos_config.id,
        })

        print("<<<< SET UP >>>>")

    def test_identify_client_field(self):
        self.assertEqual(self.pos_config.identify_client, 10.0, 
                         "The 'identify_client' field should be set to 10.0")
        print("<<<< TEST 1 >>>>")
    
    def test_pos_ui_models_to_load(self):
        models_to_load = self.pos_session._pos_ui_models_to_load()
        self.assertIn('l10n_latam.identification.type', models_to_load,
                      "The 'l10n_latam.identification.type' model should be loaded in the POS")
        print("<<<< TEST 2 >>>>")

    def test_loader_params_l10n_latam_identification_type(self):
        params = self.pos_session._loader_params_l10n_latam_identification_type()
        self.assertIn('fields', params['search_params'], "The 'fields' parameter should be in search_params")
        self.assertIn('name', params['search_params']['fields'], "The 'name' field should be in the fields list")
        self.assertIn('doc_length', params['search_params']['fields'], "The 'doc_length' field should be in the fields list")
        print("<<<< TEST 3 >>>>")
    
    def test_loader_params_res_partner(self):
        params = self.pos_session._loader_params_res_partner()
        self.assertIn('l10n_latam_identification_type_id', params['search_params']['fields'],
                      "The 'l10n_latam_identification_type_id' field should be in the fields list for res.partner")
        print("<<<< TEST 4 >>>>")

    def test_res_config_settings_identify_client(self):
        settings = self.env['res.config.settings'].create({})
        settings.pos_identify_client = 20.0
        self.assertEqual(settings.pos_identify_client, 20.0,
                         "The 'pos_identify_client' field should be set to 20.0")
        self.assertEqual(self.pos_config.identify_client, 20.0,
                         "The related 'identify_client' field in pos.config should also be 20.0")
        print("<<<< TEST 5 >>>>")
