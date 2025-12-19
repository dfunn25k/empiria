from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    l10n_pe_microenterprise_manager = fields.Boolean(
        string='Conductor Micro',
        help='El ingreso remunerativo de este empleado, será considerado como INGRESO CONDUCTOR DE MICROEMPRESA en el PLAME',
        groups="hr.group_hr_user"
    )

    is_employer = fields.Boolean(
        string='Es Empleador',
        groups="hr.group_hr_user"
    )
    employer_sign = fields.Image(
        string='Firma del empleador',
        copy=False,
        attachment=True,
        max_width=128, max_height=128,
        help='Firma del empleador, se visualizará en las boletas de los trabajadores',
        groups="hr.group_hr_user"
    )

    @api.onchange('is_employer')
    def onchange_is_employer(self):
        if not self.is_employer:
            self.employer_sign = False

    def get_employer_sign(self, company_id):
        signs = self.env['hr.employee'].search([('is_employer', '=', True), ('employer_sign', '!=', False)])

        for sign in signs:
            if sign.company_id.id == company_id.id:
                values = {
                    'name': sign.name.upper(),
                    'job_title': sign.job_title.upper() if sign.job_title else '',
                    'sign': sign.employer_sign,
                    'sign_decode': sign.employer_sign.decode('utf-8'),
                    'type_identification_id': sign.type_identification_id.name.upper() if sign.type_identification_id else '',
                    'identification_id': sign.identification_id or ''
                }
                return values
        return {}  

class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    law = fields.Text(string='Ley/Decretos')
