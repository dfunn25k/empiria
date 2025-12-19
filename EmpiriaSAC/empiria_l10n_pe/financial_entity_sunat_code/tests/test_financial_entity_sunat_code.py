from odoo.tests.common import TransactionCase


class TestFinancialEntitySunatCode(TransactionCase):

    def setUp(self):
        super(TestFinancialEntitySunatCode, self).setUp()
        self.Bank = self.env["res.bank"]

    def test_sunat_bank_code_field(self):
        """Test that the sunat_bank_code field is correctly defined and its options are correct."""
        bank = self.Bank.create(
            {
                "name": "Banco de Prueba",
                "sunat_bank_code": "02",
            }
        )
        self.assertTrue(bank, "El banco no se creó correctamente")
        self.assertEqual(
            bank.sunat_bank_code, "02", "El código Sunat no es el correcto"
        )

    def test_sunat_bank_code_selection(self):
        """Test that the selection field for sunat_bank_code contains the expected options."""
        sunat_bank_code_field = self.Bank._fields["sunat_bank_code"]
        selection_options = dict(sunat_bank_code_field.selection)
        expected_options = {
            "01": "01 - CENTRAL DE RESERVA DEL PERU",
            "02": "02 - DE CREDITO DEL PERU",
            "09": "09 - SCOTIABANK PERU",
            "99": "99 - OTROS",
        }
        for code, label in expected_options.items():
            self.assertIn(
                code,
                selection_options,
                f"El código {code} no está en las opciones de selección",
            )
            self.assertEqual(
                selection_options[code],
                label,
                f"La etiqueta para el código {code} no es la esperada",
            )
