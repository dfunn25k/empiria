from odoo import fields, models


class AirportCatalog(models.Model):
    _name = 'airport.catalog'
    _description = 'Airport Catalog'

    name = fields.Char(string='Nombre', required=True)
    code = fields.Char(string='Código', required=True)
    ubigeo = fields.Char(string='Ubigeo')
    department = fields.Char(string='Departamento')
    province = fields.Char(string='Provincia')
    district = fields.Char(string='Distrito')
    address = fields.Char(string='Dirección')
    type = fields.Char(string='Tipo')
    annexed_establishment = fields.Char(string='Establecimiento Anexo')
    vat = fields.Char(string='Número de identificación')
