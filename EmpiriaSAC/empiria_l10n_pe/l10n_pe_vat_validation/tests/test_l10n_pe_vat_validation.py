from odoo.tests import common


class TestResPartner(common.TransactionCase):

    def setUp(self):
        super(TestResPartner, self).setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'vat': '123456789',
        })

    def test_check_vat_pe_valid(self):
        """Testea que un VAT válido retorna True."""
        result = self.partner.check_vat_pe(self.partner.vat)
        self.assertTrue(result, "El VAT debería ser válido")

    def test_check_vat_pe_invalid(self):
        """Testea que un VAT vacío o inválido retorna False."""
        result = self.partner.check_vat_pe('')
        self.assertFalse(result, "El VAT vacío no debería ser válido")

    def test_check_vat_pe_none(self):
        """Testea que un VAT None retorna False."""
        result = self.partner.check_vat_pe(None)
        self.assertFalse(result, "El VAT None no debería ser válido")
