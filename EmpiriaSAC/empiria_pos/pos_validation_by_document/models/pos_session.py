from odoo import api, models


class PosSession(models.Model):
    _inherit = 'pos.session'
    
    def _loader_params_l10n_latam_identification_type(self):
        return {
            'search_params': {
                'fields': ['name', 'doc_length', 'exact_length', 'invoice_validation_document', 'is_vat'],
                'domain': [('active', '=', True)],
            },
        }
    
    def _get_pos_ui_l10n_latam_identification_type(self, params):
        return self.env['l10n_latam.identification.type'].search_read(**params['search_params'])
    
    @api.model
    def _pos_ui_models_to_load(self):
        models_to_load = super()._pos_ui_models_to_load()
        new_model = 'l10n_latam.identification.type'
        if new_model not in models_to_load:
            models_to_load.append(new_model)
        return models_to_load
    
    def _loader_params_res_partner(self):
        search_params = super()._loader_params_res_partner()
        if 'l10n_latam_identification_type_id' not in search_params['search_params']['fields']:
            search_params['search_params']['fields'].append('l10n_latam_identification_type_id')
        return search_params