# -*- coding: utf-8 -*-
from odoo import _, api, fields, models, tools
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, ValidationError
import re


class HrContractAddendumWizard(models.TransientModel):
    _name = "hr.contract.addendum.wizard"
    _description = "Asistente para Generar Adenda de Contrato"

    contract_id = fields.Many2one(
        "hr.contract",
        string="Contrato de Referencia",
        required=True,
        readonly=True,
    )

    employee_id = fields.Many2one(
        "hr.employee",
        string="Empleado",
        required=True,
        readonly=True,
    )

    template_id = fields.Many2one(
        "hr.document.template",
        string="Plantilla a Utilizar",
        required=True,
        domain="[('active', '=', True)]",
    )

    # Campos requeridos por tu documento
    relacion_laboral_date = fields.Date(
        string="Fecha de Inicio de Relación",
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string=_("Compañía"),
        required=True,
        readonly=True,
        default=lambda self: self.env.company,
        help=_(""),
    )

    clausula_modificada_ids = fields.Many2many(
        "hr.contract.clause",
        string="Cláusulas Modificadas",
    )

    # Campo para la jornada, mapea al campo técnico del contrato
    jornada_trabajo_id = fields.Many2one(
        "resource.calendar",
        string="Nueva Jornada Laboral",
        help="Selecciona la nueva jornada laboral que se reflejará en la adenda.",
    )

    suscrito_date = fields.Date(string="Fecha del Contrato Original")
    fecha_impresion = fields.Date(
        string="Fecha de Impresión",
        default=fields.Date.context_today,
    )

    @api.onchange("contract_id")
    def _onchange_contract_id(self):
        if self.contract_id:
            self.jornada_trabajo_id = self.contract_id.resource_calendar_id.id

    def _get_rendered_html(self, content_html, aliases):
        """
        Procesa un fragmento de HTML usando una lista de alias pre-cargada.
        """
        self.ensure_one()
        if not content_html:
            return ""

        eval_context = {"o": self}
        regex = re.compile(r"\[([^\]]+)\]")

        def replacer(match):
            full_match = match.group(0)
            key = match.group(1).strip()

            if full_match in aliases:
                expression = aliases[full_match]
                value = safe_eval(expression, eval_context)
                return str(value or "")
            elif key.startswith("o."):
                return f'<span t-field="{key}"/>'
            else:
                return full_match

        return re.sub(regex, replacer, content_html)

    def action_print_report(self):
        if not self.template_id:
            raise UserError(
                "Debes seleccionar una plantilla para generar el documento."
            )

        # Llama a la acción del reporte
        return self.env.ref(
            "l10n_pe_hr_contract_addendum.action_report_contract_addendum"
        ).report_action(self)
