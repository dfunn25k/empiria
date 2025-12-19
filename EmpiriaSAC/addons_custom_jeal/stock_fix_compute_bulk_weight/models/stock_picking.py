from odoo import models, fields, api

import logging
from collections import defaultdict

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.depends('move_line_ids', 'move_line_ids.result_package_id', 'move_line_ids.product_uom_id', 'move_line_ids.qty_done')
    def _compute_bulk_weight(self):
        picking_weights = defaultdict(float)
        res_groups = self.env['stock.move.line'].read_group(
            [('picking_id', 'in', self.ids), ('product_id', '!=', False), ('result_package_id', '=', False)],
            ['id:count'],
            ['picking_id', 'product_id', 'product_uom_id', 'qty_done'],
            lazy=False, orderby='qty_done asc'
        )
        products_by_id = {
            product_res['id']: (product_res['uom_id'][0], product_res['weight'])
            for product_res in
            self.env['product.product'].with_context(active_test=False).search_read(
                [('id', 'in', list(set(grp["product_id"][0] for grp in res_groups)))], ['uom_id', 'weight'])
        }
        for res_group in res_groups:
            product_id = res_group['product_id'][0]
            
            if product_id not in products_by_id:
                _logger.warning(
                    'Product %s not found in bulk weight calculation for picking %s. Skipping.',
                    product_id, res_group['picking_id'][0]
                )
                continue
            
            uom_id, weight = products_by_id[product_id]
            uom = self.env['uom.uom'].browse(uom_id)
            product_uom_id = self.env['uom.uom'].browse(res_group['product_uom_id'][0])
            picking_weights[res_group['picking_id'][0]] += (
                res_group['__count']
                * product_uom_id._compute_quantity(res_group['qty_done'], uom)
                * weight
            )
        for picking in self:
            picking.weight_bulk = picking_weights[picking.id]
