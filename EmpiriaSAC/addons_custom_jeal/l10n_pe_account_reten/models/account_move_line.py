from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    supplier_invoice_id = fields.Many2one(
        comodel_name="account.move",
        string="Factura de Proveedor",
        index=True,
        auto_join=True,
        check_company=True,
        help="Referencia a la factura del proveedor asociada a este registro. Asegura la coherencia con la compañía actual.",
    )

    supplier_invoice_name = fields.Char(
        string="Número de Factura",
        related="supplier_invoice_id.name",
        store=True,
        index=True,
        help="Número de la factura del proveedor, obtenido del campo 'name' en el modelo 'account.move'. Este campo se almacena para facilitar la búsqueda y el filtrado.",
    )

    amount_total_converted = fields.Monetary(
        string="Monto Total Convertido",
        store=True,
        default=0,
        readonly=True,
        currency_field="company_currency_id",
        help="Monto total convertido a la moneda de la compañía.",
    )
