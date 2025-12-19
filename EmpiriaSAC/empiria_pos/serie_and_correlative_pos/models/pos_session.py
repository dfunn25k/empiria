from odoo import api, fields, models


class PosSession(models.Model):
    _inherit = 'pos.session'
    
    def _loader_params_l10n_latam_document_type(self):
        return {
            'search_params': {
                'fields': ['id', 'internal_type', 'name'],
            },
        }
    
    def _get_pos_ui_l10n_latam_document_type(self, params):
        return self.env['l10n_latam.document.type'].search_read(**params['search_params'])
    
    @api.model
    def _pos_ui_models_to_load(self):
        models_to_load = super()._pos_ui_models_to_load()
        new_model = 'l10n_latam.document.type'
        if new_model not in models_to_load:
            models_to_load.append(new_model)
        return models_to_load