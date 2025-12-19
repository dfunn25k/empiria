from odoo.tests import common
from odoo.tests.common import tagged
from lxml import etree
from odoo import fields
import datetime

@tagged('post_install', '-at_install')
class TestPosConfigProduct(common.TransactionCase):
    
    def setUp(self):
        super().setUp()
                
        self.location = self.env['stock.location'].create({
            'name': 'Test Location',
        })
        self.picking_type = self.env['stock.picking.type'].create({
            'name': 'Test Picking Type',
            'default_location_src_id': self.location.id,
            'sequence_code':'100',
            'code': 'incoming'
        })
        self.pos_config = self.env['pos.config'].create({
            'name': 'Test POS Config',
            'picking_type_id': self.picking_type.id,
        })
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'product',
            'qty_available': 10,
        })
        self.pos_session = self.env['pos.session'].create({
            'name': 'Test POS Session',
            'config_id': self.pos_config.id
        })
        self.res_config_settings = self.env['res.config.settings'].create({})
        
    
    def test_location_id_related(self):
        self.assertEqual(self.picking_type.name,'Test Picking Type')
        self.assertEqual(self.picking_type.sequence_code,'100')
        self.assertEqual(self.picking_type.code,'incoming')
        self.assertEqual(self.pos_config.location_id, self.picking_type.default_location_src_id)

    def test_loader_params_product_product(self):
        search_params = self.pos_session._loader_params_product_product()
        self.assertIn('qty_available', search_params['search_params']['fields'])
        self.assertIn('type', search_params['search_params']['fields'])

    def test_pos_location_id_related(self):
        self.res_config_settings.pos_config_id = self.pos_config
        self.assertEqual(self.res_config_settings.pos_location_id, self.pos_config.location_id)