from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError


class AccountPaymentRegister(models.TransientModel):
    _name = "account.payment.register"
    _inherit = ["account.payment.register", "exchange.rate.mixin"]

    # ---------------------------------------------------------------------------- #
    #                   TODO - METODOS A HEREDAR - TIPO DE CAMBIO                  #
    # ---------------------------------------------------------------------------- #
    def _get_mixin_rate_dependencies(self):
        """
        Declara los campos que afectan el cálculo del tipo de cambio.
        Esto se usa para @api.depends en el mixin base.
        """
        return ["currency_id", "company_id", "payment_date"]

    def _get_mixin_rate_company_currency(self):
        """
        Retorna: la moneda base de la compañía.
        """
        return self.company_currency_id

    def _get_mixin_rate_currency(self):
        """
        Retorna: la moneda utilizada en la operación.
        """
        return self.currency_id

    def _get_mixin_rate_company(self):
        """
        Retorna: el registro de la compañía asociada.
        """
        return self.company_id

    def _get_mixin_rate_date(self):
        """
        Retorna: la fecha usada para el cálculo del tipo de cambio.
        """
        return self.payment_date

    # ---------------------------------------------------------------------------- #
    #                                TODO - METODOS                                #
    # ---------------------------------------------------------------------------- #
    def _add_forced_rate_to_payment_vals(self, payment_vals):
        """
        Inserta `to_force_exchange_rate` en los valores de pago si aplica.

        Requisitos:
        - La moneda de origen es la moneda de la empresa.
        - La moneda del pago es extranjera.
        - Hay una tasa forzada válida (> 0).
        """
        company_currency = self.company_id.currency_id

        # Verifica si el pago es en moneda extranjera (desde moneda base a otra).
        is_foreign_currency_payment = (
            self.source_currency_id == company_currency
            and self.currency_id != company_currency
        )

        if is_foreign_currency_payment and self.to_force_exchange_rate > 0.0:
            # Se añade la tasa forzada al diccionario del pago.
            payment_vals["to_force_exchange_rate"] = self.to_force_exchange_rate

        return payment_vals

    # ---------------------------------------------------------------------------- #
    #                           TODO - METODOS EXTENDIDOS                          #
    # ---------------------------------------------------------------------------- #
    def _get_total_amount_in_wizard_currency_to_full_reconcile(
        self, batch_result, early_payment_discount=True
    ):
        """
        Calcula el monto total en la moneda del asistente para conciliación,
        aplicando un tipo de cambio forzado si corresponde.

        :param batch_result: Resultado del procesamiento por lotes.
        :param early_payment_discount: Si se considera el descuento por pronto pago.
        :return: Tupla (monto_convertido, aplicar_descuento)
        """
        # Garantiza que el método se ejecute sobre un único registro del asistente
        self.ensure_one()

        # Obtiene la moneda de la compañía
        company_currency = self.company_id.currency_id

        # Evalúa si el pago es desde la moneda de la compañía hacia una moneda extranjera
        is_foreign_with_forced_rate = (
            self.source_currency_id == company_currency
            and self.currency_id != company_currency
            and self.to_force_exchange_rate > 0.0
        )

        # Si se cumple el caso especial de moneda extranjera y hay una tasa forzada válida
        if is_foreign_with_forced_rate:
            # Obtiene la tasa de cambio
            rate = self.to_force_exchange_rate or 1.0
            # Aplica la conversión con la tasa forzada
            converted_amount = self.source_amount * rate
            # Al usar tasa manual, se desactiva el descuento automático
            return abs(converted_amount), False

        # Lógica estándar si no aplica tipo forzado
        return super()._get_total_amount_in_wizard_currency_to_full_reconcile(
            batch_result, early_payment_discount=early_payment_discount
        )

    def _create_payment_vals_from_batch(self, batch_result):
        """
        Extiende la lógica estándar de pagos en lote para agregar tipo forzado.
        """
        self.ensure_one()
        # Obtiene los valores estándar.
        payment_vals = super()._create_payment_vals_from_batch(batch_result)
        # Llama al metodo para fozar el tipo de cambio y retorna los valores.
        return self._add_forced_rate_to_payment_vals(payment_vals)

    def _create_payment_vals_from_wizard(self, batch_result):
        """
        Extiende la lógica estándar del asistente de pago para agregar tipo forzado.
        """
        self.ensure_one()
        # Obtiene los valores estándar.
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        # Llama al metodo para fozar el tipo de cambio y retorna los valores.
        return self._add_forced_rate_to_payment_vals(payment_vals)

    # ---------------------------------------------------------------------------- #
    #                            TODO - METODOS ONCHANGE                           #
    # ---------------------------------------------------------------------------- #
    @api.onchange("to_force_exchange_rate")
    def _onchange_calculate_payment_difference(self):
        """
        Al modificar el campo `to_force_exchange_rate`, se recalcula la diferencia de pago.
        """
        self._compute_payment_difference()

    @api.onchange("line_ids")
    def _onchange_line_ids_set_forced_rate(self):
        """
        Si todas las líneas seleccionadas pertenecen a una única factura (account.move),
        se propone automáticamente su tipo de cambio forzado (`to_force_exchange_rate`)
        como valor inicial en el asistente.
        """
        # Obtener los distintos movimientos contables relacionados a las líneas
        related_moves = self.line_ids.mapped("move_id")

        if len(related_moves) == 1:
            # Si solo hay un move relacionado, usamos su tipo de cambio forzado
            self.to_force_exchange_rate = related_moves.to_force_exchange_rate or 0.0
        else:
            # Si hay múltiples moves o ninguno, limpiamos el valor
            self.to_force_exchange_rate = 0.0
