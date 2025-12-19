from odoo import api, fields, models


class HrEmployee(models.Model):

    _inherit = 'hr.employee.relative'

    address_home_id = fields.Many2one(
        'res.partner', 'Address',
    )

    right_holder = fields.Boolean(string='Derechohabiente', default=False)

    identification_id = fields.Char(string='N° identificación')

    type_identification_id = fields.Many2one(
        comodel_name="l10n_latam.identification.type",
        string='Tipo de doc.'
    )

    high_date = fields.Date(string='Fecha de alta')
    low_date = fields.Date(string='Fecha de baja')

    reason_leave = fields.Selection(selection=[
        ('02', 'Fallecimiento'),
        ('03', 'Otros motivos no previstos'),
        ('04', 'Divorcio o disolución de vínculo matrimonial'),
        ('04', 'Divorcio o disolución de vínculo matrimonial'),
        ('05', 'Fin de concubinato'),
        ('06', 'Fin de la gestación'),
        ('07', 'Hijo adquiere mayoría de edad'),
        ('08', 'Error en el registro'),
        ('09', 'Derechohabiente adquiere condición de asegurado regular'),
        ],
        string='Motivo de baja')

    document_country_id = fields.Many2one(
        comodel_name="res.country",
        string='País emisor del documento',
        groups="hr.group_hr_user"
    )

    month_pregnant = fields.Date(string='Mes de concepción')

    first_lastname = fields.Char(
        string='Apellido Paterno'
    )
    second_lastname = fields.Char(
        string='Apellido Materno'
    )

    doc_acreditation = fields.Selection(selection=[
        ('01', 'Escritura Pública'),
        ('02', 'Sentencia de Declaratoria de Paternidad'),
        ('03', 'Testamento'),
        ('04', 'Resolución de Incapacidad'),
        ('05', 'Acta o Partida de Matrimonio Civil'),
        ('06', 'Acta o Partida de Matrimonio Inscrito en Reg. Consular Peruano'),
        ('07', 'Acta o Partida de Matrimonio Realizado en el Exterior e Inscrito en la Municipalidad'),
        ('08', 'Escritura Pública - Reconoc. de Unión de Hecho - Ley N.° 29560'),
        ('09', 'Resolución Judicial - Reconc. de Unión de Hecho'),
        ('10', 'Acta de Nacimiento o Documento Análogo que Sustenta Filiación'),
        ('11', 'Declaración Jurada Existencia de Unión de Hecho'),
    ],
        string='Doc. acreditación')

    n_doc_acred = fields.Char(
        string='N° doc. acreditación',
        groups="hr.group_hr_user"
    )

    relation_type = fields.Selection(selection=[
        ('02', 'Cónyuge'),
        ('03', 'Concubina(o)'),
        ('04', 'Gestante'),
        ('05', 'Hijo Menor de Edad'),
        ('06', 'Hijo Mayor de Edad Incapacitado Permanentemente'),
    ],
        string='Vinculo')

    def action_button_right_holder(self):
        for rec in self:
            if rec.right_holder:
                return {
                    'name': 'Derecho Habiente Pariente',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'hr.employee.relative.wizard',
                    'target': 'new',
                    'context': {
                        'default_relation_id': rec.relation_id.id,
                        'default_name': rec.name,
                        'default_address_home_id': rec.address_home_id.id,
                        'default_identification_id' : rec.identification_id,
                        'default_type_identification_id': rec.type_identification_id.id,
                        'default_high_date': rec.high_date,
                        'default_low_date': rec.low_date,
                        'default_reason_leave': rec.reason_leave,
                        'default_document_country_id': rec.document_country_id.id,
                        'default_month_pregnant': rec.month_pregnant,
                        'default_first_lastname': rec.first_lastname,
                        'default_second_lastname': rec.second_lastname,
                        'default_doc_acreditation': rec.doc_acreditation,
                        'default_n_doc_acred': rec.n_doc_acred,
                        'default_relation_type': rec.relation_type,
                    },
                }
    