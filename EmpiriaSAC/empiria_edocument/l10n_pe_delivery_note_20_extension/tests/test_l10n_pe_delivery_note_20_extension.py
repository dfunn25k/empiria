from odoo.tests import common
from odoo.exceptions import AccessError


class TestL10nPeDeliveryStockPicking(common.TransactionCase):

    def setUp(self):
        super(TestL10nPeDeliveryStockPicking, self).setUp()
        self.stock_picking_model = self.env['stock.picking']
        self.airport_catalog_model = self.env['airport.catalog']
        self.port_catalog_model = self.env['port.catalog']

    def test_onchange_container_number_one(self):
        stock_picking = self.stock_picking_model.create({
            'location_id': 1,
            'location_dest_id': 2,
            'picking_type_id': 3,
            'container_number_one': 'without_container',
            'container_one_registered_number': '12345',
            'container_one_precinct_number': '6789',
        })
        print('------------CREATED STOCK------------')

        stock_picking._onchange_container_number_one()

        self.assertFalse(stock_picking.container_one_registered_number)
        self.assertFalse(stock_picking.container_one_precinct_number)
        self.assertEqual(stock_picking.container_number_two, False)
        self.assertEqual(stock_picking.container_two_registered_number, False)
        self.assertEqual(stock_picking.container_two_precinct_number, False)
        print('---------------- TEST OK --------------')

    def test_onchange_airport_catalog_id(self):
        airport_catalog = self.airport_catalog_model.create({
            'name': 'Test Airport',
            'code': 'AQP',
        })
        stock_picking = self.stock_picking_model.create({
            'airport_catalog_id': airport_catalog.id,
            'location_id': 1,
            'location_dest_id': 2,
            'picking_type_id': 3,
        })
        print('------------CREATED STOCK 2---------')

        # Trigger the onchange method
        stock_picking._onchange_airport_catalog_id()

        # Assert that the port_catalog_id has been set to False
        self.assertFalse(stock_picking.port_catalog_id)
        print('---------------- TEST 02 OK --------------')
