from odoo import _, api, fields, models, tools


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    is_analytic_account = fields.Boolean(
        related="picking_id.is_analytic_account",
        string="Es cuenta analítica?",
    )

    analytic_plan_id = fields.Many2one(
        comodel_name="account.analytic.plan",
        string="Plan analítico",
    )

    analytic_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analítico",
        domain="[('plan_id', '=', analytic_plan_id)]",
    )
