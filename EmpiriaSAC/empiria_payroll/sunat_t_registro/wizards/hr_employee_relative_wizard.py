from odoo import api, fields, models

class HrEmployeeRelativeWizard(models.TransientModel):
    _name = 'hr.employee.relative.wizard'
    _description = 'HR Employee Relative Wizard'

    address_home_id = fields.Many2one(
        'res.partner', 'Address',
    )
    
    identification_id = fields.Char(string='N° identificación')
    
    relation_id = fields.Many2one(
        "hr.employee.relative.relation",
        string="Parentesco",
        required=True
    )
    name = fields.Char(
        string="Nombre",
        required=True
    )
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

    def save_close_changes(self):

        active_ids = self.env.context.get('active_ids', [])
        relatives = self.env['hr.employee.relative'].browse(active_ids)
        for rec in self:
            for relative in relatives:
                relative.relation_id = rec.relation_id.id
                relative.name= rec.name
                relative.address_home_id = rec.address_home_id.id
                relative.identification_id = rec.identification_id
                relative.type_identification_id = rec.type_identification_id.id
                relative.high_date = rec.high_date
                relative.low_date = rec.low_date
                relative.reason_leave = rec.reason_leave
                relative.document_country_id = rec.document_country_id.id
                relative.month_pregnant = rec.month_pregnant
                relative.first_lastname = rec.first_lastname
                relative.second_lastname = rec.second_lastname
                relative.doc_acreditation = rec.doc_acreditation
                relative.n_doc_acred = rec.n_doc_acred
                relative.relation_type = rec.relation_type
        
        return {'type': 'ir.actions.act_window_close'}
        
    
    
