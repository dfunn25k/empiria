from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from unittest.mock import patch, Mock
from requests.exceptions import HTTPError, ConnectionError


class TestResCurrency(TransactionCase):
    def setUp(self):
        super(TestResCurrency, self).setUp()
        self.currency_model = self.env['res.currency']

    def test_get_api_token(self):
        icp = self.env['ir.config_parameter'].sudo()
        icp_token_1 = icp.get_param('api.access_token_first')

        tokens = self.currency_model._get_api_token()
        self.assertIn(icp_token_1, tokens)
        print(f"{'*'*20}TEST PASSED{'*'*20}")

    def test_get_api_token_no_valid_tokens(self):
        # Eliminar todos los tokens
        self.env['ir.config_parameter'].sudo().set_param('api.access_token_first', '')
        self.env['ir.config_parameter'].sudo().set_param('api.access_token', '')
        self.env['res.config.settings'].sudo().search([], limit=1).api_data_token = ''
        
        with self.assertRaises(UserError):
            self.currency_model._get_api_token()

        print(f"{'*'*20}TEST PASSED{'*'*20}")
