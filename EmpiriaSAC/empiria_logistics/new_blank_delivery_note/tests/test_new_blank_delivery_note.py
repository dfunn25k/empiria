from odoo.tests.common import TransactionCase
from datetime import datetime, timedelta


class TestNewBlankDeliveryNote(TransactionCase):

    def setUp(self):
        super(TestNewBlankDeliveryNote, self).setUp()
        self.country = self._create_or_get_country()
        self.state = self._create_or_get_state()
        self.city = self._create_or_get_city()
        self.disctrict = self.env['l10n_pe.res.city.district'].create({
                'name': 'Test District',
                'city_id': self.city.id
            })
        
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'vat': '12345678901',
            'street': 'Test Street',
            'l10n_pe_district': self.disctrict.id,
            'city_id': self.city.id,
            'state_id': self.state.id,
            'country_id': self.country.id,
        })
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'product',
            'weight': 1.5,
        })
        self.picking_type = self.env['stock.picking.type'].create({
            'name': 'Test Picking Type',
            'code': 'outgoing',
            'sequence_code': 'TEST',
        })
        self.location = self.env['stock.location'].create({
            'name': 'Test Location',
            'usage': 'internal',
        })
        self.dest_location = self.env['stock.location'].create({
            'name': 'Test Destination Location',
            'usage': 'customer',
        })

    def _create_or_get_country(self):
        Country = self.env['res.country']
        country = Country.search([('code', '=', 'TS')], limit=1)
        if not country:
            country = Country.create({
                'name': 'Test Country',
                'code': 'TS'
            })
        return country

    def _create_or_get_state(self):
        State = self.env['res.country.state']
        state = State.search([('country_id', '=', self.country.id), ('code', '=', 'TS')], limit=1)
        if not state:
            state = State.create({
                'name': 'Test State',
                'code': 'TS',
                'country_id': self.country.id
            })
        return state

    def _create_or_get_city(self):
        City = self.env['res.city']
        city = City.search([('state_id', '=', self.state.id), ('name', '=', 'Test City')], limit=1)
        if not city:
            city = City.create({
                'name': 'Test City',
                'state_id': self.state.id,
                'country_id': self.country.id
            })
        return city

    def test_generate_data_blank_delivery(self):
        operator = self.env['res.partner'].create({
                    'name': 'Test Driver',
                    'l10n_pe_edi_operator_license': 'DRV123',
                })
        
        vehicle = self.env['l10n_pe_edi.vehicle'].create({
                'name': 'Test Vehicle',
                'license_plate': 'ABC123',
                'operator_id': operator.id,
            })
        
        picking = self.env['stock.picking'].create({
            'partner_id': self.partner.id,
            'picking_type_id': self.picking_type.id,
            'location_id': self.location.id,
            'location_dest_id': self.dest_location.id,
            'date_done': datetime.now(),
            'l10n_pe_edi_departure_start_date': datetime.now() + timedelta(days=1),
            'note': 'Test Note',
            'l10n_pe_edi_observation': 'Test Observation',
            'l10n_pe_edi_transport_type': '02',
            'l10n_pe_edi_vehicle_id': vehicle.id,
            'picking_number': 'TEST0001',
        })

        self.env['stock.move.line'].create({
            'product_id': self.product.id,
            'product_uom_id': self.product.uom_id.id,
            'picking_id': picking.id,
            'location_id': self.location.id,
            'location_dest_id': self.dest_location.id,
            'qty_done': 1,
        })

        values = picking.generate_data_blank_delivery()

        self.assertEqual(values['date_done'], picking.date_done.strftime('%d/%m/%Y'))
        self.assertEqual(values['reference'], picking.name)
        self.assertEqual(values['transfer_start_date'], picking.l10n_pe_edi_departure_start_date.strftime('%d/%m/%Y'))
        self.assertEqual(values['contact'], self.partner.name)
        self.assertEqual(values['vat'], self.partner.vat)
        self.assertEqual(values['plate_number'], 'ABC123')
        self.assertEqual(values['driver_license'], 'DRV123')
        self.assertEqual(values['note'], '<p>Test Note</p> Test Observation')
        self.assertEqual(values['picking_number'], '0001')

    def test_get_aggregated_product_quantities(self):
        picking = self.env['stock.picking'].create({
            'partner_id': self.partner.id,
            'picking_type_id': self.picking_type.id,
            'location_id': self.location.id,
            'location_dest_id': self.dest_location.id,
        })

        move_line = self.env['stock.move.line'].create({
            'product_id': self.product.id,
            'product_uom_id': self.product.uom_id.id,
            'picking_id': picking.id,
            'location_id': self.location.id,
            'location_dest_id': self.dest_location.id,
            'qty_done': 1,
        })

        res = move_line._get_aggregated_product_quantities()
        
        for key, value in res.items():
            if value['product'] == self.product:
                self.assertEqual(value['weight'], self.product.weight)
                break
        else:
            self.fail("Product not found in aggregated quantities")

    def test_get_structured_address(self):
        address = self.partner.get_structured_address()
        expected_address = "Test Street, Test District, Test City, Test State, Test Country"
        self.assertEqual(address, expected_address)
