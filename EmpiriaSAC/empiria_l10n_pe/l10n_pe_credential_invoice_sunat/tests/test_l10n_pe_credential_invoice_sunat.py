from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError
from unittest.mock import patch
import json


class TestL10nPeCredentialInvoiceSunat(TransactionCase):

    def setUp(self):
        super(TestL10nPeCredentialInvoiceSunat, self).setUp()
        self.AccountMove = self.env["account.move"]
        self.company = self.env["res.company"].create(
            {
                "name": "Test Company",
                "vat": "20557912879",
                "l10n_pe_cis_client_id": "test_client_id",
                "l10n_pe_cis_client_secret": "test_client_secret",
            }
        )
        self.partner = self.env["res.partner"].create(
            {"name": "Test Partner", "vat": "20100070970"}
        )
        self.document_type = self.env["l10n_latam.document.type"].create(
            {"name": "Factura", "code": "01"}
        )
        self.move = self.AccountMove.create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_date": "2024-09-18",
                "l10n_latam_document_type_id": self.document_type.id,
                "name": "F001-00000001",
                "company_id": self.company.id,
                "amount_total": 100.00,
            }
        )

    def test_l10n_pe_cis_get_credentials(self):
        credentials = self.move._l10n_pe_cis_get_credentials(self.company)
        self.assertEqual(credentials["client_id"], "test_client_id")
        self.assertEqual(credentials["client_secret"], "test_client_secret")

    def test_l10n_pe_cis_get_credentials_missing_id(self):
        self.company.l10n_pe_cis_client_id = False
        with self.assertRaises(ValidationError):
            self.move._l10n_pe_cis_get_credentials(self.company)

    def test_l10n_pe_cis_get_credentials_missing_secret(self):
        self.company.l10n_pe_cis_client_secret = False
        with self.assertRaises(ValidationError):
            self.move._l10n_pe_cis_get_credentials(self.company)

    @patch("requests.post")
    def test_l10n_pe_cis_get_token(self, mock_post):
        mock_post.return_value.text = json.dumps({"access_token": "test_token"})
        token = self.move._l10n_pe_cis_get_token(
            {"client_id": "test_client_id", "client_secret": "test_client_secret"}
        )
        self.assertEqual(token, "test_token")

    @patch("requests.post")
    def test_l10n_pe_cis_get_token_error(self, mock_post):
        mock_post.return_value.text = json.dumps({"error_description": "Test error"})
        with self.assertRaises(ValidationError):
            self.move._l10n_pe_cis_get_token(
                {"client_id": "test_client_id", "client_secret": "test_client_secret"}
            )

    def test_l10n_pe_cis_validate_invoice_data_valid(self):
        self.move.state = "posted"
        self.move._l10n_pe_cis_validate_invoice_data()

    def test_l10n_pe_cis_validate_invoice_data_invalid_state(self):
        self.move.state = "draft"
        with self.assertRaises(ValidationError):
            self.move._l10n_pe_cis_validate_invoice_data()

    def test_l10n_pe_cis_validate_invoice_data_invalid_type(self):
        self.move.move_type = "entry"
        with self.assertRaises(ValidationError):
            self.move._l10n_pe_cis_validate_invoice_data()

    def test_l10n_pe_cis_get_invoice_number(self):
        self.assertEqual(
            self.move._l10n_pe_cis_get_invoice_number(), ["F001", "00000001"]
        )

    def test_l10n_pe_cis_get_invoice_serie(self):
        self.assertEqual(self.move._l10n_pe_cis_get_invoice_serie(), "F001")

    def test_l10n_pe_cis_get_invoice_correlative_number(self):
        self.assertEqual(self.move._l10n_pe_cis_get_invoice_correlative_number(), "1")

    def test_l10n_pe_cis_get_invoice_vat_number(self):
        self.assertEqual(self.move._l10n_pe_cis_get_invoice_vat_number(), "20557912879")

    def test_l10n_pe_cis_get_invoice_data_values(self):
        expected = {
            "numRuc": "20557912879",
            "codComp": "01",
            "numeroSerie": "F001",
            "numero": "00000001",
            "fechaEmision": "18/09/2024",
            "monto": "100.00",
        }
        self.assertEqual(self.move._l10n_pe_cis_get_invoice_data_values(), expected)

    @patch("requests.post")
    def test_action_query_integrated_cpe_sunat(self, mock_post):
        mock_post.return_value.text = json.dumps(
            {
                "success": True,
                "data": {"estadoCp": "1", "estadoRuc": "00", "condDomiRuc": "00"},
            }
        )
        self.move.action_query_integrated_cpe_sunat()
        self.assertEqual(self.move.l10n_pe_cis_cpe_status, "1")
        self.assertEqual(self.move.l10n_pe_cis_taxpayer_status, "00")
        self.assertEqual(self.move.l10n_pe_cis_taxpayer_domiciliary_status, "00")
        self.assertEqual(self.move.l10n_pe_cis_state, "confirmed")
        self.assertTrue(self.move.l10n_pe_cis_query_status)

    def test_cron_execute_query_integrated_cpe_sunat(self):
        self.move.l10n_pe_cis_state = "for_confirmed"
        self.move.state = "posted"
        with patch.object(
            TestL10nPeCredentialInvoiceSunat, "action_query_integrated_cpe_sunat"
        ) as mock_action:
            self.AccountMove._cron_execute_query_integrated_cpe_sunat()
            mock_action.assert_called_once()
