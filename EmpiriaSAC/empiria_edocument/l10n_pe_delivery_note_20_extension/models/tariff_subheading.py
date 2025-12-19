from odoo import fields, models


class TariffSubheading(models.Model):
    _name = 'tariff.subheading'
    _description = 'Tariff Subheading'

    name = fields.Char(string='Nombre', required=True)
    code = fields.Char(string='Código', required=True)
