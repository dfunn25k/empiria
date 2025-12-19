from odoo import api, fields, models


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_res_partner(self):
        search_params = super()._loader_params_res_partner()
        search_params['search_params']['fields'].extend(
            ['state_contributor_sunat', 'condition_contributor_sunat'])
        return search_params