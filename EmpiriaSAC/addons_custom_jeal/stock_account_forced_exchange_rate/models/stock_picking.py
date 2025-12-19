from odoo import _, api, fields, models


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "exchange.rate.mixin"]

    exchange_rate_date = fields.Date(
        string="Fecha del TC",
        tracking=True,
        help="Fecha utilizada para calcular el tipo de cambio. "
        "Si se define, se usará la tasa de sistema de esta fecha. "
        "Si se deja vacío y no hay tasa forzada, se usará el flujo estándar.",
    )

    # ---------------------------------------------------------------------------- #
    #                            TODO - METODOS ONCHANGE                           #
    # ---------------------------------------------------------------------------- #
    @api.onchange("exchange_rate_date")
    def _onchange_exchange_rate_date(self):
        """
        Si selecciona fecha, limpiamos el forzado.
        """
        if self.exchange_rate_date:
            self.to_force_exchange_rate = 0.0

    @api.onchange("to_force_exchange_rate")
    def _onchange_to_force_exchange_rate(self):
        """
        Si ingresa un monto forzado, limpiamos la fecha manual.
        """
        if self.to_force_exchange_rate > 0:
            self.exchange_rate_date = False

    # ---------------------------------------------------------------------------- #
    #                   TODO - METODOS A HEREDAR - TIPO DE CAMBIO                  #
    # ---------------------------------------------------------------------------- #
    def _get_mixin_rate_dependencies(self):
        """
        Declara dependencias para recalcular el TC cuando cambien estos campos.
        Esto se usa para @api.depends en el mixin base.
        """
        return [
            "company_id.currency_id",
            "purchase_id.currency_id",
            "exchange_rate_date",
        ]

    def _get_mixin_rate_company_currency(self):
        """
        Retorna: la moneda base de la compañía.
        """
        return self.company_id.currency_id

    def _get_mixin_rate_currency(self):
        """
        Retorna la moneda de la operación.
        Añadido fallback. Si no hay compra (ej. Inventario o Venta),
        devuelve la moneda de la compañía para que el TC sea 1.0 (neutro).
        """
        if self.purchase_id:
            return self.purchase_id.currency_id
        return self.company_id.currency_id

    def _get_mixin_rate_company(self):
        """
        Retorna: el registro de la compañía asociada.
        """
        return self.company_id

    def _get_mixin_rate_date(self):
        """
        Retorna: Retorna la fecha configurada en el Picking.
        """
        return self.exchange_rate_date or fields.Date.context_today(self)
