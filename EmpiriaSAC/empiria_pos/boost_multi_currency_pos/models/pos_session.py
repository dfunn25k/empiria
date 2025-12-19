from odoo import models


class PosSession(models.Model):
    _inherit = 'pos.session'
    
    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)
        currency_list = []
        dict_curr_list = {}
        
        domain = []
        if self.config_id.enable_multi_currency and not self.config_id.fetch_master and self.config_id.currencies_ids:
            domain.append(('id', 'in', self.config_id.currencies_ids.ids))
        else:
            domain.append(('active', '=', True))
        
        res_currency_ids = self.env['res.currency'].search(domain)
        
        for currency in res_currency_ids:
            vals = {
                'id': currency.id, 
                'name': currency.name,
                'rate': currency.rate,
                'rounding': currency.rounding,
                'symbol': currency.symbol,
                'position': currency.position                
            }
            dict_curr_list[currency.id] = vals
            currency_list.append(vals)
        
        loaded_data['currency_list'] = currency_list
        loaded_data['dict_curr_list'] = dict_curr_list