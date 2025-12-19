from odoo.tests.common import TransactionCase


class TestCalculateIVA(TransactionCase):

    def setUp(self):
        super(TestCalculateIVA, self).setUp()
        self.invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'currency_id': self.env.ref('base.PEN').id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Test product 1',
                'quantity': 1,
                'price_unit': 123.45,
            })],
        })
        self.invoice._compute_amount()

    def test_calculate_iva(self):
        # Calcular el IVA esperado
        expected_iva = self.invoice.amount_total / 11.0
        expected_iva = round(expected_iva, 2)

        calculated_iva = self.invoice.calculate_iva()
        self.assertEqual(calculated_iva, expected_iva, "El IVA calculado no coincide con el valor esperado")

    def test_calculate_iva_different_amount(self):
        # Test con una cantidad diferente
        self.invoice.invoice_line_ids.price_unit = 2200
        self.invoice._compute_amount()  # recompute
        expected_iva = self.invoice.amount_total / 11.0
        expected_iva = round(expected_iva, 2)
        calculated_iva = self.invoice.calculate_iva()
        self.assertEqual(calculated_iva, expected_iva, "El IVA calculado no coincide con el valor esperado para un importe diferente")