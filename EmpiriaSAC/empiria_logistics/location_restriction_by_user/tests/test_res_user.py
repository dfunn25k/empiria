from odoo.tests import common
from odoo.exceptions import UserError

class TestStockPickingUserAssignment(common.TransactionCase):

    def setUp(self):
        super(TestStockPickingUserAssignment, self).setUp()

        # Creación de usuarios
        self.user_1 = self.env['res.users'].create({
            'name': 'User 1',
            'login': 'user1',
        })
        self.user_2 = self.env['res.users'].create({
            'name': 'User 2',
            'login': 'user2',
        })

        # Creación de ubicación y asignación de usuario
        self.location_src = self.env['stock.location'].create({
            'name': 'Source Location',
            'user_ids_01': [(6, 0, [self.user_1.id])],  # Asignamos User 1 como responsable
        })
        self.location_dest = self.env['stock.location'].create({
            'name': 'Destination Location',
            'user_ids_02': [(6, 0, [self.user_2.id])],  # Asignamos User 2 como responsable
        })

        # Verificación de los nombres
        self.assertTrue(self.location_src.name, "Source Location no tiene nombre")
        self.assertTrue(self.location_dest.name, "Destination Location no tiene nombre")

        # Creación de tipo de picking y almacén
        self.warehouse = self.env['stock.warehouse'].create({
            'name': 'Test Warehouse',
            'code': 'TWH',  # Asegúrate de que el código del almacén esté presente
            'user_ids': [(6, 0, [self.user_1.id])],  # User 1 está asignado al almacén
            'view_location_id': self.env['stock.location'].create({'name': 'Test View Location', 'usage': 'view'}).id
        })


        self.picking_type = self.env['stock.picking.type'].create({
            'name': 'Test Picking Type',
            'warehouse_id': self.warehouse.id,
            'default_location_src_id': self.location_src.id,
            'default_location_dest_id': self.location_dest.id,
            'sequence_code': 'TPT',  # Añadimos el código de secuencia
            'code': 'incoming'
        })


        # Creación de picking
        self.picking = self.env['stock.picking'].create({
            'picking_type_id': self.picking_type.id,
            'location_id': self.location_src.id,
            'location_dest_id': self.location_dest.id,
            'user_logger': self.user_1.id,
        })
        print("<<<<<<<<<<<<<< SETUP >>>>>>>>>>>>>>>>>")


    def test_picking_user_assignment(self):
        
        self.assertEqual(self.picking.user_logger.id, self.user_1.id, "El usuario asignado no es correcto")

        user_logger = self.env.user.id
        expected_domain_picking_type = ['|', ('warehouse_id.user_ids', 'in', user_logger), ('warehouse_id.user_ids', '=', False)]
        
        domain_picking_type = self.picking.fields_view_get(view_type='form')['fields']['picking_type_id']['domain']
        
        evaluated_domain_picking_type = eval(domain_picking_type.replace('user_logger', str(user_logger)))
        
        self.assertEqual(expected_domain_picking_type, evaluated_domain_picking_type,
                        "El dominio para picking_type_id no es correcto")

        expected_domain_location = ['|', ('user_ids_01', 'in', 1), ('user_ids_01', '=', False)]
        
        domain_location = self.picking.fields_view_get(view_type='form')['fields']['location_id']['domain']
        print(expected_domain_location,"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        print(domain_location,"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        
        self.assertEqual(expected_domain_location, eval(domain_location),
                        "El dominio para location_id no es correcto")

        print("<<<<<<<<<<<<<< TEST 1 >>>>>>>>>>>>>>>>>")


    def test_button_validate_with_responsible_user(self):
        self.picking.write({'location_dest_id': self.location_dest.id})

        self.picking.location_dest_id.write({'user_ids_02': [(6, 0, [self.user_2.id])]})
        
        self.picking.write({'user_logger': self.user_2.id})
        
        print(f"Usuarios responsables de la ubicación destino: {self.picking.location_dest_id.user_ids_02}")
        print(f"Usuario logger actual: {self.picking.user_logger}")

        self.picking.button_validate()  

        print("<<<<<<<<<<<<<< TEST 2 >>>>>>>>>>>>>>>>>")





