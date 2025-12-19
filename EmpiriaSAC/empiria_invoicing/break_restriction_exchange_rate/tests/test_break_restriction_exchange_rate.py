from odoo.tests.common import TransactionCase


class TestBreakRestrictionExchangeRate(TransactionCase):

    def setUp(self):
        super(TestBreakRestrictionExchangeRate, self).setUp()
        # Crear una compañía y una moneda de ejemplo
        self.company = self.env['res.company'].create({
            'name': 'Test Company',
        })
        self.currency = self.env['res.currency'].create({
            'name': 'TEST',
            'symbol': 'T',
            'rounding': 0.01,
        })

    def test_verification_constraint_removed(self):
        """ Test that the unique constraint is removed, allowing two rates on the same day. """
        ResCurrencyRate = self.env['res.currency.rate']

        # Crear la primera tasa de cambio en la misma fecha
        ResCurrencyRate.create({
            'name': '2024-08-22',
            'currency_id': self.currency.id,
            'rate': 1.2,
            'company_id': self.company.id,
        })

        # Crear la segunda tasa de cambio en la misma fecha
        # Esto debería funcionar sin errores si la restricción se ha eliminado
        rate2 = ResCurrencyRate.create({
            'name': '2024-08-22',
            'currency_id': self.currency.id,
            'rate': 1.5,
            'company_id': self.company.id,
        })

        self.assertEqual(rate2.name, '2024-08-22', "La tasa de cambio se creó correctamente para la misma fecha.")
