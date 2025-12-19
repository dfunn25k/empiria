from odoo import api, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.model
    def get_floors(self, kwargs):
        
        if len(kwargs.get('other_config')):
            pos_config_info = self.env['pos.config'].browse(kwargs.get('other_config'))
            restaurant_installed = False
            
            for config in pos_config_info:
                if config.module_pos_restaurant:
                    restaurant_installed = True

            if restaurant_installed:
                floors = self.env['restaurant.floor'].search([('pos_config_id', 'in', kwargs.get('other_config'))])
                data = []
                for floor in floors:
                    table_ids = []
                    for table_id in floor.table_ids:
                        table_ids.append(table_id.id)
                    data.append({
                        'id': floor.id,
                        'name': floor.name,
                        'background_color': floor.background_color,
                        'table_ids': table_ids,
                        'sequence': floor.sequence,
                        'pos_config_id': floor.pos_config_id.id
                    })
                return data
            else:
                return False

    @api.model
    def get_tables(self, kwargs):
        
        if len(kwargs.get('other_config')):
            pos_config_info = self.env['pos.config'].browse(kwargs.get('other_config'))
            restaurant_installed = False
            
            for config in pos_config_info:
                if config.module_pos_restaurant:
                    restaurant_installed = True

            if restaurant_installed:
                floors_ids = []
                floors = self.env['restaurant.floor'].search([('pos_config_id', 'in', kwargs.get('other_config'))])
                for floor in floors:
                    floors_ids.append(floor.id)
                tables = self.env['restaurant.table'].search([('floor_id', 'in', floors_ids)])
                data = []
                for table in tables:
                    data.append({
                        'id': table.id,
                        'name': table.name,
                        'display_name': table.display_name,
                        'floor_id': table.floor_id.id,
                        'color': table.color,
                        'active': table.active,
                    })
                return data
            else:
                return False