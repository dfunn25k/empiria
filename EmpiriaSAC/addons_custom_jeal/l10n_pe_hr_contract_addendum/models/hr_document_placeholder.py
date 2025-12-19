# -*- coding: utf-8 -*-
from odoo import _, api, fields, models, tools


class HrDocumentPlaceholder(models.Model):
    _name = "hr.document.placeholder"
    _description = "Alias de Placeholder para Documentos de RRHH"
    _order = "name"

    name = fields.Char(
        string="Placeholder (Alias)",
        required=True,
        help="El alias completo que usarás, ej: [NOMBRE_TRABAJADOR]",
    )

    expression = fields.Char(
        string="Expresión de Reemplazo (Python)",
        required=True,
        help="La expresión a evaluar para obtener el texto. Ej: o.employee_id.name",
    )

    description = fields.Char(
        string="Descripción",
    )

    _sql_constraints = [
        ("name_uniq", "unique (name)", "¡El placeholder debe ser único!")
    ]
