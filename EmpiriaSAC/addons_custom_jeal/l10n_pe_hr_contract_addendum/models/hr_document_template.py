# -*- coding: utf-8 -*-
from odoo import models, fields


class HrDocumentTemplate(models.Model):
    _name = "hr.document.template"
    _description = "Plantilla de Documento de RRHH"

    name = fields.Char(
        string="Nombre de la Plantilla",
        required=True,
    )

    active = fields.Boolean(
        string="Activo",
        default=True,
    )

    line_ids = fields.One2many(
        "hr.document.template.line",
        "template_id",
        string="Cláusulas del Documento",
    )
