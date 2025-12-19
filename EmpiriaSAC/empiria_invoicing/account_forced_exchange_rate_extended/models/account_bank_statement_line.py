from odoo import _, api, fields, models
from collections import defaultdict


class AccountBankStatementLine(models.Model):
    _name = "account.bank.statement.line"
    _inherit = ["account.bank.statement.line", "exchange.rate.mixin"]

    # related_invoice_id = fields.Many2one(
    #     comodel_name="account.move",
    #     string=_("Factura relacionada"),
    #     tracking=True,
    #     domain="""[
    #         ('company_id', '=', company_id),
    #         ('move_type', 'in', ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']),
    #         ('state', '=', 'posted'),
    #         ('payment_state', '=', 'in_payment'),
    #         ('partner_id', '=', partner_id)
    #     ]""",
    #     help=_(
    #         "Factura contable relacionado del cual se puede obtener "
    #         "una tasa de cambio de referencia para el asiento bancario."
    #     ),
    # )

    # ---------------------------------------------------------------------------- #
    #                   TODO - METODOS A HEREDAR - TIPO DE CAMBIO                  #
    # ---------------------------------------------------------------------------- #
    def _get_mixin_rate_dependencies(self):
        """
        Declara los campos que afectan el cálculo del tipo de cambio.
        Esto se usa para @api.depends en el mixin base.
        """
        return ["company_id", "currency_id", "date"]

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
        return self.date

    # ---------------------------------------------------------------------------- #
    #                           TODO - METODOS EXTENDIDOS                          #
    # ---------------------------------------------------------------------------- #
    # TODO - METODO PARA CREAR Y ESCRIBIR
    def _get_amounts_with_currencies(self):
        """
        Extiende la lógica estándar para recalcular el importe en la moneda de la
        compañía (`company_amount`) cuando se utiliza una tasa de cambio forzada.
        Este importe es el que finalmente se registra en el asiento contable.
        """
        self.ensure_one()

        # Obtener los valores base desde la implementación estándar.
        (
            company_amount,
            company_currency,
            journal_amount,
            journal_currency,
            transaction_amount,
            foreign_currency,
        ) = super()._get_amounts_with_currencies()

        # Preparar la tasa forzada (si aplica).
        rate = self.to_force_exchange_rate or 0.0

        # Recalcula el monto en moneda de la compañía si existe:
        #   - Un tipo de cambio externo.
        #   - Las monedas (diario, compañía) difieren.
        is_foreign_payment_with_forced_rate = (
            foreign_currency == journal_currency
            and journal_currency != company_currency
            and rate > 0.0
        )

        if is_foreign_payment_with_forced_rate:
            # Conversión DIVIDIENDO si la fuente es moneda local.
            new_company_amount = journal_amount / rate
            # Redondeo con la precisión de la moneda de la compañía.
            company_amount = company_currency.round(new_company_amount)

        # Retornar todos los valores ajustados (o estándar si no aplica).
        return (
            company_amount,
            company_currency,
            journal_amount,
            journal_currency,
            transaction_amount,
            foreign_currency,
        )

    def _synchronize_to_moves(self, changed_fields):
        """
        Extiende la lógica de sincronización entre la línea de extracto bancario y su asiento contable.

        Reglas:
        - Solo ciertos campos disparan la sincronización.
        - Si se modifica `to_force_exchange_rate`, se trata como si también se hubiese modificado `amount`,
        para forzar el recálculo contable.

        :param changed_fields: Lista de nombres de campos modificados.
        """
        if self._context.get("skip_account_move_synchronization"):
            return

        # Convertimos a set para facilitar operaciones de conjunto.
        changed_fields_set = set(changed_fields)

        # Forzar sincronización si cambia la tasa de cambio forzada.
        if "to_force_exchange_rate" in changed_fields_set:
            changed_fields_set.add("amount")

        # Lista blanca de campos que activan sincronización.
        trigger_fields = {
            "payment_ref",
            "amount",
            "amount_currency",
            "foreign_currency_id",
            "currency_id",
            "partner_id",
        }

        # Si ningún campo relevante ha cambiado, abortar.
        if not (changed_fields_set & trigger_fields):
            return

        # Llamada al método original con los campos permitidos.
        return super()._synchronize_to_moves(list(changed_fields_set))

    # ---------------------------------------------------------------------------- #
    #                             TODO - METODOS ACCION                            #
    # ---------------------------------------------------------------------------- #
    @api.model_create_multi
    def create(self, vals_list):
        """
        Extiende el método estándar `create()` para propagar automáticamente la tasa de
        cambio forzada (`to_force_exchange_rate`) desde las líneas del extracto bancario
        hacia sus respectivos asientos contables (`account.move`).
        """
        # 1. Crear las líneas utilizando la lógica estándar.
        statement_lines = super().create(vals_list)

        # Diccionario para agrupar los asientos contables por tasa de cambio.
        # La clave: Es la tasa.
        # El valor: Es un conjunto de moves (recordsets).
        moves_by_rate = defaultdict(lambda: self.env["account.move"])

        # Recorrer las líneas creadas y recolectar los asientos que necesitan actualización.
        for st_line in statement_lines.filtered(
            lambda line: line.to_force_exchange_rate > 0.0
            and line.move_id
            and not line.foreign_currency_id
        ):
            moves_by_rate[st_line.to_force_exchange_rate] |= st_line.move_id

        # Actualizar los asientos en lote según la tasa correspondiente.
        for rate, moves in moves_by_rate.items():
            moves.write({"to_force_exchange_rate": rate})

        return statement_lines

    # ---------------------------------------------------------------------------- #
    #                            TODO - METODOS COMPUTE                            #
    # ---------------------------------------------------------------------------- #
    @api.depends(
        "company_id",
        "currency_id",
        "date",
        "amount",
        "foreign_currency_id",
        "to_force_exchange_rate",
    )
    def _compute_amount_currency(self):
        """
        Calcula el valor en moneda extranjera (`amount_currency`) para líneas de extracto bancario,
        considerando si se usa una tasa de cambio forzada, una moneda extranjera, o se debe delegar
        al comportamiento estándar.
        """
        for st_line in self:
            # Si no hay moneda extranjera definida, no se calcula
            if not st_line.foreign_currency_id:
                st_line.amount_currency = False
                continue

            # Si hay tasa forzada y la moneda extranjera difiere de la moneda contable
            if (
                st_line.to_force_exchange_rate > 0
                and st_line.foreign_currency_id != st_line.currency_id
            ):
                st_line.amount_currency = (
                    st_line.amount / st_line.to_force_exchange_rate
                )

            # Si la moneda extranjera coincide con la moneda contable
            elif st_line.foreign_currency_id == st_line.currency_id:
                st_line.amount_currency = st_line.amount

            # Si no se cumplen los casos anteriores, aplicar la lógica estándar
            else:
                super(AccountBankStatementLine, st_line)._compute_amount_currency()

    # ---------------------------------------------------------------------------- #
    #                            TODO - METODOS ONCHANGE                           #
    # ---------------------------------------------------------------------------- #
    # @api.onchange("partner_id")
    # def _onchange_related_invoice_id(self):
    #     """
    #     Borra la factura relacionada si cambia el partner para evitar inconsistencia de datos.
    #     """
    #     self.related_invoice_id = False
