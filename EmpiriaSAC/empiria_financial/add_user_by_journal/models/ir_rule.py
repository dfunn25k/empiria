from odoo import api, models, tools
from odoo.osv import expression
from odoo.tools import config


class IrRule(models.Model):
    _inherit = "ir.rule"

    @api.model
    @tools.conditional(
        "xml" not in config["dev_mode"],
        tools.ormcache(
            "self.env.uid",
            "self.env.su",
            "model_name",
            "mode",
            "tuple(self._compute_domain_context_values())",
        ),
    )
    def _compute_domain(self, model_name, mode="read"):
        """
        This function is used to compute the domain of the ir.rule.
        It is used to restrict the records that are accessible to the user.
        The function uses the ormcache decorator to cache the result of the function based on the user's id and the model name.
        If the user is not an administrator, the function adds an extra domain to restrict the records based on the journal_assign_to_ids field.
        The function uses the expression.AND function to combine the extra domain with the original domain.
        """
        res = super()._compute_domain(model_name, mode=mode)
        user = self.env.user
        if model_name == "account.move" and not user.has_group("add_user_by_journal.res_groups_admin_journal_access"):
            extra_domain = [[('journal_assign_to_ids', 'in', [user.id])]]
            res = expression.AND(extra_domain + [res])
        return res
