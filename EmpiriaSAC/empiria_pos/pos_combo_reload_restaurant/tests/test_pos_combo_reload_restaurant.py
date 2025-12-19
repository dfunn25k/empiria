import json
from odoo.tests.common import TransactionCase

class TestPosComboReloadRestaurant(TransactionCase):

    def setUp(self):
        super(TestPosComboReloadRestaurant, self).setUp()

        self.product_1 = self.env['product.product'].create({
            'name': 'Product 1',
            'list_price': 10.0
        })
        self.product_2 = self.env['product.product'].create({
            'name': 'Product 2',
            'list_price': 15.0
        })
        
        self.pos_session = self.env['pos.session'].create({
            'config_id': self.env.ref('point_of_sale.pos_config_main').id,
        })
        # Crear orden con líneas de combo
        self.order_data = {
            'session_id': self.pos_session.id,
            'lines': [
                (0, 0, {'product_id': self.product_1.id, 'qty': 1, 'order_menu': '[{"products": [{"product_id": %d, "qty": 1}] }]' % self.product_1.id, 'is_selection_combo': True}),
                (0, 0, {'product_id': self.product_2.id, 'qty': 1, 'order_menu': '[{"products": [{"product_id": %d, "qty": 1}] }]' % self.product_1.id, 'is_selection_combo': True}),
                (0, 0, {'product_id': self.product_1.id, 'qty': 1, 'order_menu': False, 'is_selection_combo': False}),
            ]
        }

        self.pos_order = self.env['pos.order'].create({
            'session_id': self.pos_session.id,
            'amount_tax': 0.0,
            'amount_total': 0.0,
            'amount_paid': 0.0,
            'amount_return': 0.0,
        })
        print("<<<<<< SET UP >>>>>>")

    def test_order_lines_combo(self):

        orders = [self.order_data]

        for line in orders[0]['lines']:
            if line[2]['order_menu']:
                line[2]['order_menu'] = json.loads(line[2]['order_menu'])
        
        self.pos_order._order_lines_combo(orders)
        
        self.assertEqual(len(orders[0]['lines']), 2, "La línea combinada duplicada debe eliminarse")
        print("<<<<< TEST 1 >>>>>")

    def test_prepare_order_line(self):

        order_line = {
            'order_menu': "[{'products': [{'product_id': %d, 'qty': 1}] }]" % self.product_1.id,
            'own_data': "{'custom_data': 'value'}",
        }
        prepared_line = self.pos_order._prepare_order_line(order_line)
        
        # Verificar que el campo 'order_menu' ha sido procesado correctamente
        self.assertIsInstance(prepared_line['order_menu'], list, "Order menu deberia ser evaluado como una lista")
        self.assertIsInstance(prepared_line['own_data'], dict, "Los datos propios deben evaluarse como un diccionario")
        print("<<<<< TEST 2 >>>>>>")

