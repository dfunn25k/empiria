from odoo import api, fields, models, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    use_expired_contract = fields.Boolean(
        string='Incluir contratos Expirados',
        help='Si marcas esta Casilla, al momento de “Generar Recibos de nómina”, Odoo seleccionará a todos los empleados que hayan tenido algún contrato cuyas fechas están comprendidas en el “Periodo Forzado” seleccionado, sin importar si dichos contrato están actualmente vencidos o archivados.'
    )
    date_start_contract = fields.Date(
        string='Periodo de contrato inicio',
        states={'draft': [('readonly', False)]}, 
        default=lambda self: fields.Date.to_string(date.today().replace(day=1))
    )
    date_end_contract = fields.Date(
        string='Periodo de contrato fin',
        states={'draft': [('readonly', False)]},
        default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date())
    )

    @api.constrains('date_start_contract', 'date_end_contract')
    def _check_contract_dates(self):
        for record in self:
            if record.date_end_contract < record.date_start_contract:
                raise UserError(_('La fecha de fin del contrato no puede ser anterior a la fecha de inicio.'))
