from odoo import fields, models, api

class PleInvBalLines(models.Model):
    _name = 'ple.report.inv.bal.line.one'
    _description = 'Efectivo y Equivalente de efectivo - Líneas'
    _order = 'sequence desc'

    period = fields.Char(string="Periodo")
    accounting_account = fields.Char(string="Cuenta contables")
    bank_account_name = fields.Char(string="Nombre de la cuenta bancaria")
    type_currency = fields.Char(string="Tipo de Moneda")
    balance = fields.Float(string="Saldo")
    credit_balance = fields.Float(string="Saldo acreedor", compute="_onchange_credit_balance")
    debit_balance = fields.Float(string="Saldo Deudor", compute="_onchange_debit_balance")
    status = fields.Char(string="Estado")
    note = fields.Char(string="Nota")
    bic = fields.Char(string="Codigo de la Entidad Financiera")
    account_bank_code = fields.Char(string="Número de la cuenta de la Entidad Financiera")
    sequence = fields.Integer(string='Secuencia')

    ple_report_inv_val_one_id = fields.Many2one(
        comodel_name='ple.report.inv.bal.one',
        string='Reporte de Estado de Situación financiera'
    )

    account_ids = fields.Many2many(
        comodel_name='account.move.line',
        string='Cuentas',
        readonly=1
    )

    @api.depends('balance')
    def _onchange_credit_balance(self):
        for record in self:
            record.credit_balance = record.balance if record.balance <= 0.00 else 0.00

    @api.depends('balance')
    def _onchange_debit_balance(self):
        for record in self:
            record.debit_balance = record.balance if record.balance > 0.00 else 0.00