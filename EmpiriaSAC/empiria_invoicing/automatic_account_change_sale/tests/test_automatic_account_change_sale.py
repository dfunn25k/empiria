from odoo.tests.common import TransactionCase
from datetime import date

dat = date.today()

class TestAutomaticAccountChangeSale(TransactionCase):
    def setUp(self):
        super(TestAutomaticAccountChangeSale, self).setUp()
        self.model_move = self.env['account.move']
        self.account_model = self.env['account.account']
        self.account_change_by_type_model = self.env['account.change.by.type']

        # Crear la moneda
        self.currency_id_usd = self.env.ref("base.USD")
        self.currency_id_eur = self.env.ref("base.EUR")

        # Crear el diario
        self.journal_id_usd = self.env['account.journal'].create({
            'name': 'Diario Venta USD',
            'type': 'sale',
            'code': 'TestD',
            'currency_id': self.currency_id_usd.id,
        })

        # Crear el diario
        self.journal_id_eur = self.env['account.journal'].create({
            'name': 'Diario Venta EUR',
            'type': 'sale',
            'code': 'TestE',
            'currency_id': self.currency_id_usd.id,
        })

        # Crear cuentas
        self.acc_vent_1 = self.account_model.create({
            'name': 'Venta 1',
            'code': '1224',
            'account_type': 'asset_receivable',
            'company_id': self.env.ref("base.main_company").id,
        })

        self.acc_vent_2 = self.account_model.create({
            'name': 'Venta 2',
            'code': '1225',
            'account_type': 'asset_receivable',
            'company_id': self.env.ref("base.main_company").id,
        })

        self.acc_purch = self.account_model.create({
            'name': 'Compra',
            'code': '1223',
            'account_type': 'liability_payable',
            'company_id': self.env.ref("base.main_company").id,
        })

        # Crear el registro de cambio de cuenta
        self.account_change_usd = self.account_change_by_type_model.create({
            'journal_id': self.journal_id_usd.id,
            'currency_id': self.currency_id_usd.id,
            'sale_account_id': self.acc_vent_1.id,
            'purchase_account_id': self.acc_purch.id,
            'company_id': self.env.ref("base.main_company").id,
        })

         # Crear el registro de cambio de cuenta
        self.account_change_eur = self.account_change_by_type_model.create({
            'journal_id': self.journal_id_eur.id,
            'currency_id': self.currency_id_eur.id,
            'sale_account_id': self.acc_vent_2.id,
            'purchase_account_id': self.acc_purch.id,
            'company_id': self.env.ref("base.main_company").id,
        })
        
        print('--------TEST - Cambio de cuenta creado OK-------')

    def test_automatic_account_change_sale(self):
        # Crear un movimiento contable con líneas de diario
        account_move_1 = self.model_move.create({
            'date': dat,
            'state': 'draft',
            'move_type': 'entry',
            'company_id': self.env.ref("base.main_company").id,
            'journal_id': self.journal_id_usd.id,
            'currency_id': self.currency_id_usd.id,
            'line_ids': [
                (0, 0, {
                    'account_id': self.acc_vent_1.id,
                    'debit': 100.0,
                    'credit': 0.0,
                    'name': 'Cuenta por cobrar'
                }),
                (0, 0, {
                    'account_id': self.acc_purch.id,
                    'debit': 0.0,
                    'credit': 100.0,
                    'name': 'Compra'
                }),
            ]
        })

        # Crear un movimiento contable con líneas de diario
        account_move_2 = self.model_move.create({
            'date': dat,
            'state': 'draft',
            'move_type': 'entry',
            'company_id': self.env.ref("base.main_company").id,
            'journal_id': self.journal_id_eur.id,
            'currency_id': self.currency_id_eur.id,
            'line_ids': [
                (0, 0, {
                    'account_id': self.acc_vent_2.id,
                    'debit': 100.0,
                    'credit': 0.0,
                    'name': 'Cuenta por cobrar'
                }),
                (0, 0, {
                    'account_id': self.acc_purch.id,
                    'debit': 0.0,
                    'credit': 100.0,
                    'name': 'Compra'
                }),
            ]
        })

        self.assertTrue(account_move_1)
        self.assertTrue(account_move_2)
        print('--------TEST - Creación exitosa OK-------')

        # Aplicar cambio automático de cuenta
        account_move_1._get_change_account()
        account_move_2._get_change_account()
        
        # Obtener las cuentas esperadas después del cambio
        expected_sale_account_usd = self.account_change_usd.sale_account_id
        expected_sale_account_eur = self.account_change_eur.sale_account_id

        # Verificar las cuentas de las líneas del diario
        sale_lines_usd = account_move_1.line_ids.filtered(lambda l: l.account_id.id == expected_sale_account_usd.id)
        sale_lines_eur = account_move_2.line_ids.filtered(lambda l: l.account_id.id == expected_sale_account_eur.id)
        
        for line in sale_lines_usd:
            print(f'Cuenta por cobrar (USD) asignada: {line.account_id.id} - {line.account_id.name}')
            self.assertEqual(
                line.account_id.id, 
                expected_sale_account_usd.id, 
                f"La cuenta por cobrar  asignada ({line.account_id.name}) no coincide con la esperada ({expected_sale_account_usd.name}) después de forzar el cambio"
            )
        for line in sale_lines_eur:
            print(f'Cuenta por pagar (EUR) asignada: {line.account_id.id} - {line.account_id.name}')
            self.assertEqual(
                line.account_id.id, 
                expected_sale_account_eur.id, 
                f"La cuenta por pagar asignada ({line.account_id.name}) no coincide con la esperada ({expected_sale_account_eur.name}) después de forzar el cambio"
            )

        print(f'Cuenta por cobrar (USD) esperada: {expected_sale_account_usd.id} - {expected_sale_account_usd.name}')
        print(f'Cuenta por pagar (EUR) esperada: {expected_sale_account_eur.id} - {expected_sale_account_eur.name}')
        print('--------TEST - Cambio automático de cuenta para venta - OK-------')





        




