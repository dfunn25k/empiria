from odoo import api, fields, models


class PosSession(models.Model):
    _inherit = 'pos.session'
    
    def _loader_params_hr_employee(self):
        search_params = super()._loader_params_hr_employee()
        search_params['search_params']['fields'].extend(["pos_access_close", "pos_access_delete_order",
        "pos_access_delete_orderline", "pos_access_decrease_quantity", "pos_access_discount",
        "pos_access_payment", "pos_access_price"])
        return search_params