from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    account_number_partner_id = fields.Many2one(
        comodel_name="res.partner.bank",
        string="Número de cuenta de Proveedor",
        options={"no_create": True},  # Evitar la creación de nuevos registros
    )

    currency_partner_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda del Proveedor",
        related="account_number_partner_id.currency_id",
        readonly=False,
        options={"no_create": True},  # Evitar la creación de nuevos registros
    )

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        self.account_number_partner_id = False
