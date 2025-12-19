from odoo import api, fields, models

class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    l10n_pe_afp = fields.Boolean(
        string='Excluir de Base AFP',
        help='Marcar en reglas de código BSP_001 que no se deben tomar en cuenta como base AFP en excel AFPNet.',
        default=False,
    )