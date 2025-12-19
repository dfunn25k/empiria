from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    is_analytic_account = fields.Boolean(
        string="Es cuenta analítica?",
        default=False,
        help="Indica si se puede modificar una cuenta analítica",
    )
