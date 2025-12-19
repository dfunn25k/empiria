from odoo.tests.common import TransactionCase
from datetime import date

dat = date.today()

class TestAutomaticAccountChangePurchase(TransactionCase):
    def setUp(self):
        super(TestAutomaticAccountChangePurchase, self).setUp()
        self.model_move = self.env['account.move']
        self.account_model = self.env['account.account']
        self.account_change_by_type_model = self.env['account.change.by.type']
        self.purchase_order_model = self.env['purchase.order']
        self.product_model = self.env['product.product']
        self.picking_model = self.env['stock.picking']

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

        self.journal_id_eur = self.env['account.journal'].create({
            'name': 'Diario Venta EUR',
            'type': 'sale',
            'code': 'TestE',
            'currency_id': self.currency_id_eur.id,
        })

        # Crear cuentas

        self.acc_vent = self.account_model.create({
            'name': 'Venta',
            'code': '1225',
            'account_type': 'asset_receivable',
            'create_asset':'draft',
            'company_id': self.env.ref("base.main_company").id,
        })

        self.acc_purch_1 = self.account_model.create({
            'name': 'Compra Test 1',
            'code': '1223',
            'account_type': 'liability_payable',
            'create_asset':'draft',
            'company_id': self.env.ref("base.main_company").id,
        })

        self.acc_purch_2 = self.account_model.create({
            'name': 'Compra Test 2',
            'code': '1224',
            'account_type': 'liability_payable',
            'create_asset':'draft',
            'company_id': self.env.ref("base.main_company").id,
        })

        # Crear el registro de cambio de cuenta
        self.account_change_usd = self.account_change_by_type_model.create({
            'journal_id': self.journal_id_usd.id,
            'currency_id': self.currency_id_usd.id,
            'sale_account_id': self.acc_vent.id,
            'purchase_account_id': self.acc_purch_1.id,
            'company_id': self.env.ref("base.main_company").id,
        })

        self.account_change_eur = self.account_change_by_type_model.create({
            'journal_id': self.journal_id_eur.id,
            'currency_id': self.currency_id_eur.id,
            'sale_account_id': self.acc_vent.id,
            'purchase_account_id': self.acc_purch_2.id,
            'company_id': self.env.ref("base.main_company").id,
        })

        # Crear producto para la orden de compra
        self.product = self.product_model.create({
            'name': 'Test Product',
            'type': 'product',
            'list_price': 100.0,
            'standard_price': 100.0,
        })

        self.partner = self.env["res.partner"].create({
            "name": "Test Customer",
            "property_account_receivable_id": self.account_change_usd.purchase_account_id.id,
        })

        # Crear una orden de compra
        self.purchase_order = self.purchase_order_model.create({
            'partner_id': self.partner.id,
            'date_order': dat,
            'currency_id': self.currency_id_usd.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'name': 'Test Product',
                'product_qty': 1.0,
                'price_unit': 100.0,
            })],
        })

        # Confirmar la orden de compra
        self.purchase_order.button_confirm()
        self.picking_id = self.picking_model.search([('purchase_id', '=', self.purchase_order.id)], limit=1)
        for operation in self.picking_id.move_ids_without_package:
            operation.write({'quantity_done':1})
            self.picking_id.button_validate()

        # Crear factura relacionada con la orden de compra
        invoice_action = self.purchase_order.action_create_invoice()
        self.invoice = self.model_move.browse(invoice_action['res_id'])
        self.invoice._get_change_account()

        print('--------TEST - Preparación OK-------')

    def test_automatic_account_change_purchase(self):
        # Crear un movimiento contable con líneas de diario en USD
        account_move_1 = self.model_move.create({
            'date': dat,
            'state': 'draft',
            'move_type': 'entry',
            'company_id': self.env.ref("base.main_company").id,
            'journal_id': self.journal_id_usd.id,
            'currency_id': self.currency_id_usd.id,
            'line_ids': [
                (0, 0, {
                    'account_id': self.acc_vent.id,
                    'debit': 100.0,
                    'credit': 0.0,
                    'name': 'Cuenta por cobrar'
                }),
                (0, 0, {
                    'account_id': self.acc_purch_1.id,
                    'debit': 0.0,
                    'credit': 100.0,
                    'name': 'Compra'
                }),
            ]
        })

        # Crear un movimiento contable con líneas de diario en EUR
        account_move_2 = self.model_move.create({
            'date': dat,
            'state': 'draft',
            'move_type': 'entry',
            'company_id': self.env.ref("base.main_company").id,
            'journal_id': self.journal_id_eur.id,
            'currency_id': self.currency_id_eur.id,
            'line_ids': [
                (0, 0, {
                    'account_id': self.acc_vent.id,
                    'debit': 100.0,
                    'credit': 0.0,
                    'name': 'Cuenta por cobrar'
                }),
                (0, 0, {
                    'account_id': self.acc_purch_2.id,
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
        expected_purchase_account_usd = self.account_change_usd.purchase_account_id
        expected_purchase_account_eur = self.account_change_eur.purchase_account_id

        # Verificar las cuentas de las líneas del diario para USD
        purchase_lines_usd = account_move_1.line_ids.filtered(lambda l: l.account_id == expected_purchase_account_usd)
        self.assertGreater(len(purchase_lines_usd), 0, "No se encontraron líneas con la cuenta esperada para USD")
        
        for line in purchase_lines_usd:
            print(f'Cuenta por cobrar (USD) asignada: {line.account_id.id} - {line.account_id.name}')
            self.assertEqual(
                line.account_id.id, 
                expected_purchase_account_usd.id, 
                f"La cuenta por cobrar asignada ({line.account_id.name}) no coincide con la esperada ({expected_purchase_account_usd.name}) después de forzar el cambio"
            )

        # Verificar las cuentas de las líneas del diario para EUR
        purchase_lines_eur = account_move_2.line_ids.filtered(lambda l: l.account_id == expected_purchase_account_eur)
        self.assertGreater(len(purchase_lines_eur), 0, "No se encontraron líneas con la cuenta esperada para EUR")
        
        for line in purchase_lines_eur:
            print(f'Cuenta por pagar (EUR) asignada: {line.account_id.id} - {line.account_id.name}')
            self.assertEqual(
                line.account_id.id, 
                expected_purchase_account_eur.id, 
                f"La cuenta por pagar asignada ({line.account_id.name}) no coincide con la esperada ({expected_purchase_account_eur.name}) después de forzar el cambio"
            )

        print(f'Cuenta esperada en la factura: {expected_purchase_account_usd.id} - {expected_purchase_account_usd.name}')
        print(f'Cuenta esperada en la factura: {expected_purchase_account_eur.id} - {expected_purchase_account_eur.name}')
        print('--------TEST - Cambio automático de cuenta en factura OK-------')






        




