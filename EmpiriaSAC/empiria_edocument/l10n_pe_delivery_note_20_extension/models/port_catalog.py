from odoo import fields, models


class PortCatalog(models.Model):
    _name = 'port.catalog'
    _description = 'Port Catalog'

    name = fields.Char(string='Nombre', required=True)
    code = fields.Char(string='Código', required=True)
    ubigeo = fields.Char(string='Ubigeo')
    department = fields.Char(string='Departamento')
    province = fields.Char(string='Provincia')
    district = fields.Char(string='Distrito')
    address = fields.Char(string='Dirección')
    state = fields.Char(string='Estado')
