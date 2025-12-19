from odoo import _, api, fields, models
from odoo.tools.float_utils import float_round, float_is_zero, float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    # ---------------------------------------------------------------------------- #
    #                           TODO - METODOS HEREDADOS                           #
    # ---------------------------------------------------------------------------- #
    def _get_currency_convert_date(self):
        """
        Sobrescribe la fecha utilizada para seleccionar la tasa de cambio
        aplicada en movimientos de inventario relacionados con compras.

        Prioridad aplicada:
            1. Movimientos donde aplica lógica estándar (devoluciones o sin PO).
            2. Fecha manual definida en el picking (exchange_rate_date).
            3. Fecha estándar definida por Odoo.

        :return: Fecha a utilizar para conversión de moneda.
        :rtype: date
        """
        self.ensure_one()

        # Caso 1: Devoluciones u operaciones sin línea de compra → comportamiento estándar.
        if self._should_ignore_pol_price():
            return super()._get_currency_convert_date()

        convert_date = super()._get_currency_convert_date()
        print("convert_date", convert_date)

        # Caso 2: Si el usuario configuró una fecha manual de tipo de cambio en el picking → usar fecha personalizada.
        if self.picking_id and self.picking_id.exchange_rate_date:
            convert_date = self.picking_id.exchange_rate_date
        print("picking_id", convert_date)

        # Caso 3: Si no se cumple ninguna condición anterior → usar lógica estándar.
        return convert_date

    def _get_price_unit(self):
        """
        Calcula el precio unitario del movimiento utilizando una tasa de cambio
        personalizada (si ha sido configurada en el picking). Si no existe dicha
        configuración, se mantiene el cálculo base de Odoo.

        Flujo aplicado:
            1. Respeta comportamiento estándar para devoluciones o movimientos sin PO.
            2. Obtiene precio estándar calculado por Odoo.
            3. Verifica si existen configuraciones del usuario (exchange_rate / forced_rate).
            4. Si aplica, revierte el cálculo estándar y aplica nuevamente usando la tasa forzada.

        :return: Precio unitario calculado con o sin tasa de cambio personalizada.
        :rtype: float
        """
        self.ensure_one()

        # Caso 1: Devoluciones o movimientos sin compra → usar el cálculo estándar.
        if self._should_ignore_pol_price():
            return super()._get_price_unit()

        # Precio calculado normalmente por Odoo (en moneda de compañía).
        price_unit_origin = super()._get_price_unit()

        # Si no está vinculado a un picking → no puede aplicar cálculo custom.
        if not self.picking_id:
            return price_unit_origin

        picking = self.picking_id

        # Determina si hay configuración personalizada de tasa de cambio.
        has_forced_rate = bool(
            picking.to_force_exchange_rate > 0 or picking.exchange_rate_date
        )
        if not has_forced_rate:
            return price_unit_origin

        # ---------------------------------------------------------------------------- #
        #                          LÓGICA DE REEMPLAZO DE TASA                         #
        # ---------------------------------------------------------------------------- #
        # Se obtiene información relevante de la línea de compra.
        line = self.purchase_line_id
        order = line.order_id
        company = order.company_id

        # Si ambas monedas son iguales → no convertir nada.
        if order.currency_id == company.currency_id:
            return price_unit_origin

        # Precisión definida en configuración de Odoo.
        precision = self.env["decimal.precision"].precision_get("Product Price")

        # ----------------------------- RE-CÁLCULO CUSTOM ---------------------------- #
        # Fecha usada originalmente por Odoo para la conversión.
        conversion_date = self._get_currency_convert_date()

        # Obtiene la tasa que Odoo usó para hacer la conversión original.
        rate_odoo = order.currency_id._get_conversion_rate(
            order.currency_id, company.currency_id, company, conversion_date
        )

        # Si por alguna razón Odoo devolvió 0 → evitar división por cero.
        if rate_odoo == 0:
            return price_unit_origin

        # Paso A: Deshacer conversión original (volver al valor en moneda extranjera).
        price_in_foreign_currency = price_unit_origin / rate_odoo

        # Paso B: Aplicar tasa forzada configurada por el usuario.
        if picking.exchange_rate:
            new_price_unit = price_in_foreign_currency * picking.exchange_rate

            # Ajusta según precisión configurada en Odoo.
            return float_round(new_price_unit, precision_digits=precision)

        # Si no aplica tasa → retornar el valor oriignal.
        return price_unit_origin

    def _generate_valuation_lines_data(
        self,
        partner_id,
        qty,
        debit_value,
        credit_value,
        debit_account_id,
        credit_account_id,
        svl_id,
        description,
    ):
        """
        Genera los valores contables de valoración (Stock Valuation) aplicando una
        tasa de cambio personalizada si fue configurada en el picking.

        Este método extiende el comportamiento estándar para ajustar el campo
        `amount_currency` en el asiento contable de inventario cuando:
            - La operación proviene de una orden de compra.
            - La moneda de la orden es distinta a la moneda compañía.
            - Existe una tasa de cambio forzada > 0 en el picking.

        Si la tasa se define solo por fecha, el proceso estándar ya calcula correctamente.

        :return: Diccionario con valores contables ajustados o estándar.
        :rtype: dict
        """
        self.ensure_one()

        # Ejecuta la lógica estándar y obtiene la estructura contable base.
        valuation_data = super(StockMove, self)._generate_valuation_lines_data(
            partner_id,
            qty,
            debit_value,
            credit_value,
            debit_account_id,
            credit_account_id,
            svl_id,
            description,
        )

        purchase_line = self.purchase_line_id
        picking = self.picking_id

        # No aplica: movimientos sin línea de compra o sin picking.
        if not purchase_line or not picking:
            return valuation_data

        order = purchase_line.order_id

        # No aplica si ambas monedas son iguales.
        if order.currency_id == self.company_id.currency_id:
            return valuation_data

        # Solo intervenimos si hay un valor forzado (> 0).
        # Si fue por 'Fecha', el metodo 'def _get_currency_convert_date(self):' ya lo calculó bien.
        forced_rate = picking.to_force_exchange_rate
        if forced_rate <= 0:
            return valuation_data

        # ---------------------------------------------------------------------------- #
        #                     AJUSTE DE MONTO EN MONEDA EXTRANJERA                     #
        # ---------------------------------------------------------------------------- #
        valuation_layer = self.env["stock.valuation.layer"].browse(svl_id)
        precision = self.env["decimal.precision"].precision_get("Product Price")

        # Modificar solo asientos contables estándar (evitar ajustes o landed costs).
        if not valuation_layer.account_move_line_id:
            # Balance contable ya en moneda local.
            credit_balance = valuation_data["credit_line_vals"]["balance"]
            debit_balance = valuation_data["debit_line_vals"]["balance"]

            # Conversión: moneda local → moneda extranjera usando tasa forzada.
            # Fórmula: Soles / Tasa = Dólares
            # Ejemplo: 380 Soles / 3.80 = 100 USD
            new_credit_currency = float_round(
                credit_balance / picking.exchange_rate, precision_digits=precision
            )
            new_debit_currency = float_round(
                debit_balance / picking.exchange_rate, precision_digits=precision
            )

            # Reemplazo del monto en moneda extranjera.
            valuation_data["credit_line_vals"]["amount_currency"] = new_credit_currency
            valuation_data["debit_line_vals"]["amount_currency"] = new_debit_currency

        return valuation_data
