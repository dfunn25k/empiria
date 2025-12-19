# -*- coding: utf-8 -*-
from odoo import models, fields


class HrDocumentTemplateLine(models.Model):
    """
    Representa una línea o cláusula dentro de una plantilla de documento.
    Cada línea se clasifica como encabezado, contenido o pie de página.
    """

    _name = "hr.document.template.line"
    _description = "Línea de Plantilla de Documento de RRHH"
    _order = "sequence, id"

    # --- Campos de Estructura y Orden ---
    sequence = fields.Integer(
        string="Secuencia",
        default=10,
    )
    
    template_id = fields.Many2one(
        comodel_name="hr.document.template",
        string="Plantilla",
        required=True,
        ondelete="cascade",
    )
    
    # CAMBIO: Nuevo campo para definir la sección del documento.
    display_type = fields.Selection(
        selection=[
            ("header", "Encabezado"),
            ("content", "Contenido (Cláusula)"),
            ("footer", "Pie de Página"),
        ],
        string="Tipo de Sección",
        required=True,
        default="content",
        help="Define en qué parte del documento se mostrará esta línea:\n"
        "- Encabezado: Para logos, títulos o información de la empresa.\n"
        "- Contenido: Para las cláusulas numeradas del contrato.\n"
        "- Pie de Página: Para firmas, fechas o información legal.",
    )

    # Se vuelven opcionales aquí, su obligatoriedad se controla en la vista.
    clausula_id = fields.Many2one(
        comodel_name="hr.contract.clause",
        string="Cláusula",
    )
    
    title = fields.Char(
        string="Título",
        help="Ej: DE LA RELACIÓN LABORAL",
    )

    # --- Campo de Contenido General ---
    content = fields.Html(
        string="Contenido",
        help="Contenido de la sección. Puedes usar placeholders como [NOMBRE_TRABAJADOR] "
        "para reemplazo dinámico en el reporte.",
    )
