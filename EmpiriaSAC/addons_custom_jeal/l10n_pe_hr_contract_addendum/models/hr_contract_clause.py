# -*- coding: utf-8 -*-
from odoo import models, fields


class HrContractClause(models.Model):
    _name = "hr.contract.clause"
    _description = "Cláusula de Contrato"
    _order = "sequence"

    name = fields.Char(
        string="Nombre de la Cláusula",
        required=True,
    )

    sequence = fields.Integer(
        string="Secuencia",
        default=10,
    )
