from odoo import models


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)
        documents_by_id = []

        documents_by_ids = self.env['l10n_latam.identification.type'].search([('active', '=', True)])

        for document in documents_by_ids:
            vals = {
                'id': document.id,
                'name': document.name
            }
            documents_by_id.append(vals)

        loaded_data['documents_by_id'] = documents_by_id

    def _loader_params_res_partner(self):
        search_params = super()._loader_params_res_partner()
        if 'l10n_latam_identification_type_id' not in search_params['search_params']['fields']:
            search_params['search_params']['fields'].append('l10n_latam_identification_type_id')
        return search_params
