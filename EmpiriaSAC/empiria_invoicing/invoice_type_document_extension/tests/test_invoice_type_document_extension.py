from odoo.tests import common
from odoo.tests import Form
import logging

_logger = logging.getLogger(__name__)

@common.tagged('post_install', '-at_install')
class TestInvoiceTypeDocumentExtension(common.TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.country_pe = self.env['res.country'].search([('code', '=', 'PE')])
        self.partner =  self.env['res.partner'].create({
            'name': 'Comapny Ga',
            'email': 'company@enterprise.com',
            'country_id':self.country_pe.id
        })
        

    def test_module_installed(self):
        module = self.env['ir.module.module'].search([('name', '=', 'invoice_type_document_extension')])
        self.assertTrue(module.state == 'installed','Modulo no instalado')
        _logger.info("Module installed successfully")


    def test_computed_fields(self):

        warehouse = self.env['stock.warehouse'].search([], limit=1)
        warehouse.write({'reception_steps': 'three_steps'})
        warehouse.mto_pull_id.route_id.active = True
        self.env['stock.location']._parent_store_compute()
        warehouse.reception_route_id.rule_ids.filtered(
            lambda p: p.location_src_id == warehouse.wh_input_stock_loc_id and
                      p.location_dest_id == warehouse.wh_qc_stock_loc_id).write({
            'procure_method': 'make_to_stock'
        })

        picking = self.env['stock.picking'].create({
            "name": "WH/TEST/0001",
            'partner_id':self.partner.id,
            "picking_type_id": 2,
            "location_id": 2,
            "location_dest_id": 3,
            "state":"draft"    
        })
     
        picking.picking_number = '233-1232323'
        self.assertEqual(picking.serie_transfer_document, '233')
        self.assertEqual(picking.number_transfer_document, '1232323')
        
        picking.picking_number = False
                
        self.assertEqual(picking.serie_transfer_document, False)
        self.assertEqual(picking.number_transfer_document, False)
        _logger.info("invoice_type_document_extension TEST OK")
