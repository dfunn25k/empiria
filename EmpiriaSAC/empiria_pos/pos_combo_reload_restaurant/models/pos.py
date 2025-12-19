from odoo import models


class PosOrder(models.Model):
    _inherit = "pos.order"

    def _get_fields_for_order_line(self):
        fields = super(PosOrder, self)._get_fields_for_order_line()
        fields.extend(['order_menu', 'own_data', 'is_selection_combo', 'worthless_combo'])
        return fields

    @staticmethod
    def _order_lines_combo(orders):
        print('ENVIA DEL BACK AL FRONT LAS ORDENES')
        """
            Funcion captura y elimina las lineas repetidas que son generadas por un producto combo
            Esta funcion se llama cuando se presiona una mesa en pos frontend y hacer query al backend
        Args:
            orders: ordenes del backend
        Returns:
            ordenes hacia el frontend pos
        """
        for order in orders:
            list_combo = []
            list_del = []
            if order.get("lines", False):
                # Cap
                for num, line in enumerate(order['lines']):
                    if line[2]['is_selection_combo'] and line[2]['order_menu']:
                        for products in line[2]['order_menu']:
                            list_combo += products['products']
                    else:
                        # this line exist in list_destruction, compare a product_id and qty
                        for count, del_elem in enumerate(list_combo):
                            if line[2]['product_id'] == del_elem['product_id'] and int(line[2]['qty']) == del_elem['qty']:
                                list_del.append(order['lines'][num])
                                list_combo.pop(count)
                # delete
                for element in list_del:
                    if element in order['lines']:
                        order['lines'].remove(element)

    def _prepare_order_line(self, order_line):
        order_line = super()._prepare_order_line(order_line)
        order_line['order_menu'] = eval(order_line['order_menu']) if order_line['order_menu'] else False
        order_line['own_data'] = eval(order_line['own_data']) if order_line['own_data'] else False
        return order_line

    def _get_order_lines(self, orders):
        super(PosOrder, self)._get_order_lines(orders)
        self._order_lines_combo(orders)
