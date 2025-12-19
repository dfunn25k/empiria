from odoo import fields, models


class IdentificationCodeTaxConcept(models.Model):
    _name = 'identification.code.tax.concept'
    _description = 'Identification Code Tax Concept'

    name = fields.Char(string='Nombre', required=True)
    code = fields.Char(string='Código', required=True)
