from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
import json


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_analytic_account = fields.Boolean(
        related="picking_type_id.is_analytic_account",
        string="Es cuenta analítica?",
    )

    analytic_plan_id = fields.Many2one(
        comodel_name="account.analytic.plan",
        string="Planes analíticos",
    )

    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Cuentas analíticas",
        domain="[('plan_id', '=', analytic_plan_id)]",
    )

    stock_move_line_nosuggest_ids = fields.One2many(
        "stock.move.line",
        "picking_id",
        domain=[
            "|",
            ("reserved_qty", "=", 0.0),
            "&",
            ("reserved_qty", "!=", 0.0),
            ("qty_done", "!=", 0.0),
        ],
    )

    stock_move_line_ids_without_package = fields.One2many(
        "stock.move.line",
        "picking_id",
        domain=[
            "|",
            ("package_level_id", "=", False),
            ("picking_type_entire_packs", "=", False),
        ],
    )

    def button_add_analytic_account(self):
        success_message = "Se modificaron las cuentas analíticas correctamente."
        error_lines = []

        for record in self:
            if record.show_reserved != True:
                move_line_ids = record.stock_move_line_nosuggest_ids
            else:
                move_line_ids = record.stock_move_line_ids_without_package

            try:
                stock_move_line_ids = self.env["stock.move.line"].search(
                    [
                        ("id", "in", move_line_ids.ids),
                        ("analytic_id", "!=", False),
                    ]
                )

                for move_line in stock_move_line_ids:
                    analytic_id = move_line.analytic_id.id

                    valuation_layer_ids = self.env["stock.valuation.layer"].search(
                        [
                            ("stock_move_id", "=", move_line.move_id.id),
                        ]
                    )

                    for layer in valuation_layer_ids:
                        product_category = layer.product_id.categ_id
                        if product_category:
                            stock_account_output = (
                                product_category.property_stock_account_output_categ_id
                            )

                            relevant_lines = layer.account_move_id.line_ids.filtered(
                                lambda line: line.account_id == stock_account_output
                            )

                            for line in relevant_lines:
                                line.analytic_distribution = {str(analytic_id): 100}
            except Exception as e:
                error_lines.append(move_line.id)
                # logger.error("Error al modificar las cuentas analíticas: %s" % str(e))

        if error_lines:
            error_message = (
                "Se produjeron errores al modificar las cuentas analíticas en las líneas con ID: %s"
                % ", ".join(str(line_id) for line_id in error_lines)
            )
            raise ValidationError(error_message)
        else:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Éxito",
                    "message": success_message,
                    "sticky": False,
                },
            }

    def button_add(self):
        for record in self:
            if not record.analytic_account_id:
                raise ValidationError(
                    "Debe especificar una cuenta analítica para este registro."
                )

            if record.show_reserved != True:
                move_line_ids = record.stock_move_line_nosuggest_ids
            else:
                move_line_ids = record.move_line_ids_without_package

            stock_move_line_ids = self.env["stock.move.line"].search(
                [
                    ("id", "in", move_line_ids.ids),
                ]
            )

            analytic_plan_id = record.analytic_plan_id.id
            analytic_id = record.analytic_account_id.id

            for line in stock_move_line_ids:
                line.write(
                    {
                        "analytic_plan_id": analytic_plan_id,
                        "analytic_id": analytic_id,
                    }
                )
