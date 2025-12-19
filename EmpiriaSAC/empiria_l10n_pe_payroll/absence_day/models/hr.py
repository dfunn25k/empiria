from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
import pytz


class HRContractUpdateWizard(models.TransientModel):
    _name = "hr.contract.update.wizard"
    _description = "Wizard to update fields on contracts"

    date_generated_from = fields.Date(
        string='Desde',
        required=True
    )
    date_generated_to = fields.Date(
        string='hasta',
        required=True
    )

    def action_update_hr_contract_fields(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''
        contract_ids = self.env['hr.contract'].browse(active_ids)
        contract_ids.generate_work_entries(self.date_generated_from, self.date_generated_to, force=True)


class HRContract(models.Model):
    _inherit = "hr.contract"

    def action_open_hr_contract_update_wizard(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''
        return {
            'context': self.env.context,
            'name': 'Actualizar campos en contrato',
            'res_model': 'hr.contract.update.wizard',
            'view_mode': 'form',
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def generate_work_entries_cron_method(self):
        now = datetime.now()
        init_date = datetime(now.year, now.month, 1).date()
        last_day = (datetime.now() + relativedelta(day=1, months=+1, days=-1)).date()
        contract_ids = self.env['hr.contract'].search([
            ('state', '=', 'open')
        ])
        contract_ids.generate_work_entries(init_date, last_day, force=True)


class HrWorkEntryType(models.Model):
    _inherit = 'hr.work.entry.type'

    name = fields.Char(translate=True)
