from odoo import models, fields, api
from datetime import datetime
import pytz


class CertificateEmployee(models.Model):
    _inherit = 'hr.employee'

    date_today = fields.Char(string='Fecha', compute='_date_today')

    def search_employee(self):
        return self.env['hr.employee'].search([('is_employer', '=', True)], limit=1)

    def _date_today(self):
        tz = self.env.user.tz or 'UTC'
        local_time = datetime.now(pytz.timezone(tz))
        date = local_time.strftime('%d de %B de %Y')
        self.date_today = date

    def get_date_to_print(self):
        add_l = self.date_today.split(' ')
        add_l[-2] = 'del'
        add_l = ' '.join(add_l)
        return add_l

    def print_report(self):
        return self.env.ref('job_certificate_employee.report_job_certification_employee').report_action(docids=None)
