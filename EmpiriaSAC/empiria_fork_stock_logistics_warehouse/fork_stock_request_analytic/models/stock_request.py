from odoo import api, fields, models


class StockRequest(models.Model):
    _inherit = "stock.request"
    _check_company_auto = True

    analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Analytic Account",
        check_company=True,
    )

    @api.onchange("product_id")
    def onchange_product_id(self):
        """
        Set default analytic account on lines from order if defined.
        """
        res = super().onchange_product_id()
        if self.order_id and self.order_id.default_analytic_account_id:
            self.analytic_account_id = self.order_id.default_analytic_account_id
        return res

    def _prepare_procurement_values(self, group_id=False):

        """
        Add analytic account to procurement values
        """
        res = super()._prepare_procurement_values(group_id=group_id)
        if self.analytic_account_id:
            res.update({"analytic_account_id": self.analytic_account_id.id})
        return res
