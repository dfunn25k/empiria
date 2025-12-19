from odoo import models, fields



class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_multi_currency = fields.Boolean(
        string="Enable MultiCurrency"
    )
    display_conversion = fields.Boolean(
        string="Enable Display Conversion"
    )
    fetch_master = fields.Boolean(
        string="Fetch All Active Currencies"
    )
    currencies_ids = fields.Many2many(
        comodel_name='res.currency',
        relation='rel_pos_currencies',
        column1='currency_id',
        column2='config_id',
        string='Currency'
    )