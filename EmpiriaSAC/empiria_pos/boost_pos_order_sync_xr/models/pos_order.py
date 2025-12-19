from odoo import api, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _get_fields_for_draft_order(self):
        fields = super()._get_fields_for_draft_order()
        fields.append('quote_id')
        return fields

    @api.model
    def get_table_draft_orders(self, table_ids):
        table_orders = super().get_table_draft_orders(table_ids)
        for order in table_orders:
            if order.get('quote_id'):
                quote_id = order['quote_id'][0]
                quote_name = order['quote_id'][1]
                order['quote_id'] = quote_id
                order['quote_name'] = quote_name
        return table_orders
