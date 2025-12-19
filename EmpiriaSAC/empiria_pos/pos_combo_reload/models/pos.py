from odoo import api, fields, models
from functools import partial

class PosSession(models.Model):
    _inherit = 'pos.session'
    
    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)
        topping_item_by_id = {}

        topping_item_ids = self.env['product.selection.topping'].search([])
        
        for topping in topping_item_ids:
            vals = {
                'id': topping.id, 
                'product_categ_id': topping.product_categ_id.id,
                'multi_selection': topping.multi_selection,
                'product_ids': [topping.product_ids.ids],
                'no_of_min_items': topping.no_of_min_items,
                'no_of_items': topping.no_of_items,
                'description': topping.description
            }
            topping_item_by_id[topping.id] = vals
        
        loaded_data['topping_item_by_id'] = topping_item_by_id
    
    def _loader_params_product_product(self):
        search_params = super()._loader_params_product_product()
        search_params['search_params']['fields'].extend(['is_selection_combo', 'product_topping_ids', 'include_price', 'is_editable_items'])
        return search_params
    

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _order_fields(self, ui_order):
        print('ENVIA DEL FRONT AL BACK LAS ORDENES')
        """
            Extension de funcionalidad nativa, procesa las ordenes que vienen del front como lo hace odoo nativo en el
            modulo point_of_sale modificando las "lines" (ordenes) para agregar el atributo own_line que ha sido creado
            en el front
        Args:
            ui_order: ordenes del front
        Returns:
            ordenes con atributo own_line hacia el backend

        """
        res = super(PosOrder, self)._order_fields(ui_order)
        process_line = partial(self.env['pos.order.line'].with_context(add_own_line=True)._order_line_fields, session_id=ui_order['pos_session_id'])
        order_lines = [process_line(line) for line in ui_order['lines']] if ui_order['lines'] else False        
        new_order_line = []
        if order_lines:
            for order_line in order_lines:
                if order_line:
                    new_order_line.append(order_line)
                    if 'own_line' in order_line[2]:
                        own_pro_list = [process_line(line) for line in order_line[2]['own_line']] if order_line[2]['own_line'] else False
                        if own_pro_list:
                            for own in own_pro_list:
                                new_order_line.append(own)
        if new_order_line:
            for order_line in range(len(new_order_line)):
                if len(ui_order['lines']) > order_line:
                    if ui_order['lines'][order_line] and ui_order['lines'][order_line][2].get('sale_order_origin_id'):
                        new_order_line[order_line][2]['sale_order_origin_id'] = ui_order['lines'][order_line][2]['sale_order_origin_id']
                    if ui_order['lines'][order_line][2].get('sale_order_line_id'):
                        new_order_line[order_line][2]['sale_order_line_id'] = ui_order['lines'][order_line][2]['sale_order_line_id']
            process_line = partial(self.env['pos.order.line']._order_line_fields, session_id=ui_order['pos_session_id'])
            order_lines = [process_line(line) for line in new_order_line]
            res['lines'] = order_lines
        return res


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    is_selection_combo = fields.Boolean(
        string='Selection Combo Line'
    )
    order_menu = fields.Text(
        string='Order Menu'
    )
    own_data = fields.Text(
        string='Order Data'
    )
    worthless_combo = fields.Boolean(
        default=False
    )

    def _export_for_ui(self, orderline):
        export_ui = super()._export_for_ui(orderline)
        export_ui['order_menu'] = eval(orderline.order_menu) if orderline.order_menu else []
        export_ui['own_data'] = eval(orderline.own_data) if orderline.own_data else []
        export_ui['worthless_combo'] = orderline.worthless_combo
        return export_ui
    
    def _order_line_fields(self, line, session_id=None):
        own_line = []
        if line and 'own_line' in line[2] and self.env.context.get('add_own_line', False):
            own_line = line[2]['own_line']

        line = super(PosOrderLine, self)._order_line_fields(line, session_id=session_id)

        if own_line:
            line[2]['own_line'] = own_line
        return line