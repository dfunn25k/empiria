from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from odoo import fields

class TestPosDeliveryOrder(TransactionCase):

    def setUp(self):
        super(TestPosDeliveryOrder, self).setUp()

        # Crear un partner de prueba
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'street': '123 Main Street',
            'city': 'Lima',
            'zip': '15000',
            'country_id': self.env.ref('base.pe').id,  # Asignar el país
        })

        # Crear la configuración de POS
        self.pos_config = self.env['pos.config'].create({
            'name': 'Test POS',
            'company_id': self.env.company.id,  # Asignar la empresa actual
            'is_posbox': False,  # No es un POS Box
            'picking_type_id': self.env.ref('stock.picking_type_out').id,  # Tipo de operación de entrega
        })

        # Crear una sesión de punto de venta asociada al POS configurado
        self.session = self.env['pos.session'].create({
            'config_id': self.pos_config.id,  # Vincular con la configuración de POS
        })

        # Crear un usuario para realizar entregas
        self.delivery_person = self.env['res.users'].create({
            'name': 'Delivery Person',
            'login': 'delivery_person@example.com',
        })

        # Crear el pedido de entrega
        self.delivery_order = self.env['pos.delivery.order'].create({
            'partner_id': self.partner.id,
            'person_id': self.delivery_person.id,
            'order_no': 'DO-001',
            'delivery_date': fields.Datetime.now(),
            'order_date': fields.Datetime.now(),
            'session_id': self.session.id,  # Asignar la sesión creada
            'address': self.partner.street,
        })
        print("<<<<< SET UP COMPLETED >>>>>")

    def test_delivery_order_creation(self):
        self.assertTrue(self.delivery_order)
        self.assertEqual(self.delivery_order.state, 'draft')
        print("<<<<<< TEST DELIVERY ORDER CREATION PASSED >>>>>>>")

    def test_delivery_order_state_change(self):
        self.delivery_order.make_in_progress()
        self.assertEqual(self.delivery_order.state, 'in_progress')

        self.delivery_order.make_delivered()
        self.assertEqual(self.delivery_order.state, 'delivered')
        print("<<<<< TEST DELIVERY ORDER STATE CHANGE PASSED >>>>>>")
