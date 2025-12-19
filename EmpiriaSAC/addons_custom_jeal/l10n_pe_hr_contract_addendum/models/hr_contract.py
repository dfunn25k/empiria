# -*- coding: utf-8 -*-
from odoo import models, fields


class HrContract(models.Model):
    _inherit = "hr.contract"

    def action_open_addendum_wizard(self):
        """
        Abre el wizard para generar del contrato.
        """
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Generar Contrato",
            "res_model": "hr.contract.addendum.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_contract_id": self.id,
                "default_employee_id": self.employee_id.id,
            },
        }
