from odoo import api, fields, models



class PosSession(models.Model):
    _inherit = 'pos.session'
    
    def _loader_params_product_product(self):
        search_params = super()._loader_params_product_product()
        search_params['search_params']['fields'].extend(['qty_available', 'type'])
        return search_params