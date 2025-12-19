from odoo import models


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        search_params = super()._loader_params_product_product()
        search_params['search_params']['fields'].extend(["list_price"])  # price #is_home_delivery_charge
        return search_params

    def _loader_params_res_partner(self):
        search_params = super()._loader_params_res_partner()
        search_params['search_params']['fields'].append("street2")
        return search_params

    def _loader_params_pos_payment_method(self):
        search_params = super()._loader_params_pos_payment_method()
        search_params['search_params']['fields'].append("is_home_delivery")
        return search_params

    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)
        list_users = []
        users = self.env['res.users'].search([])
        for user in users:
            list_users.append({'id': user.id, 'name': user.name})
        loaded_data['users_total_by_id'] = list_users
