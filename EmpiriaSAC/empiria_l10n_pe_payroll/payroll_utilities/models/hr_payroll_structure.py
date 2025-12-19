from odoo import fields, models


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    not_utilities_day_lines = fields.Boolean(string='No Incluir días en Utilidades', help='Si marcas este campo, los registros de días de los recibos de nómina de esta estructura, NO se tomarán en cuenta para calcular el Total de días trabajados para utilidades, a pesar de que en el "Tipo de entrada de trabajo" indiques que se toma en cuenta para utilidades.')