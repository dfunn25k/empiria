from odoo.tests.common import TransactionCase

class TestResConfigSettings(TransactionCase):

    def setUp(self):
        super(TestResConfigSettings, self).setUp()
        self.ResConfigSettings = self.env['res.config.settings']

    def test_api_data_token(self):
        # Crear un nuevo record de configuración
        config = self.ResConfigSettings.create({
            'api_data_token': 'RAcSGWD1TgC7VdjCTOZSVA==',
        })

        # Guardar la configuración
        config.execute()

        # Verificar que el valor se ha guardado correctamente en ir.config_parameter
        param = self.env['ir.config_parameter'].get_param('api.access_token')
        self.assertEqual(param, 'RAcSGWD1TgC7VdjCTOZSVA==')

        # Verificar que el valor por defecto es correcto
        config_default = self.ResConfigSettings.default_get(['api_data_token'])
        self.assertEqual(config_default['api_data_token'], 'RAcSGWD1TgC7VdjCTOZSVA==')


        print('--------------TEST API DATA TOKEN OK--------------')