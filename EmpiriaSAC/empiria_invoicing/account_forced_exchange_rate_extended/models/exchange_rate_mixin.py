from odoo import _, api, fields, models, tools


class ExchangeRateMixin(models.AbstractModel):
    """
    Mixin reutilizable para la gestión avanzada del tipo de cambio en modelos Odoo.

    Este mixin permite calcular un tipo de cambio personalizado, ya sea forzado por el usuario
    o automático según la fecha, moneda y empresa. Utiliza el patrón "Template Method",
    delegando la obtención de datos específicos al modelo que lo hereda.
    """

    _name = "exchange.rate.mixin"
    _description = "Mixin para Gestión de Tipo de Cambio"
    _abstract = True

    # ---------------------------------------------------------------------------- #
    #                                 TODO - CAMPOS                                #
    # ---------------------------------------------------------------------------- #
    exchange_rate = fields.Float(
        string=_("Tipo de Cambio"),
        digits=0,
        compute="_compute_exchange_rate",
        store=True,
        tracking=True,
        readonly=True,
        help=_(
            "Tasa de cambio utilizada para esta operación. Puede estar forzada o calculada automáticamente"
        ),
    )

    to_force_exchange_rate = fields.Float(
        string=_("Forzar Tipo de Cambio"),
        digits=0,
        tracking=True,
        help=_("Este campo se utiliza para forzar el tipo de cambio en la operación"),
    )

    # ---------------------------------------------------------------------------- #
    #                     TODO - METODOS A HEREDAR OBLIGATORIO                     #
    # ---------------------------------------------------------------------------- #
    def _get_mixin_rate_dependencies(self):
        """
        Retorna una lista de nombres de campos que afectan el cálculo del tipo de cambio.

        Este método puede ser sobrescrito por modelos heredados para declarar dependencias
        adicionales en el decorador @api.depends.

        Ejemplo: ['currency_id', 'company_id', 'date']
        """
        return []

    def _get_mixin_rate_company_currency(self):
        """
        Retorna la moneda base de la compañía (ej. self.company_id.currency_id).
        """
        raise NotImplementedError(
            _(
                "Debe implementar el método '_get_mixin_rate_company_currency' para obtener el tipo de cambio."
            )
        )

    def _get_mixin_rate_currency(self):
        """
        Retorna la moneda de la operación (ej. self.currency_id).
        """
        raise NotImplementedError(
            _(
                "Debe implementar el método '_get_mixin_rate_currency' para obtener el tipo de cambio."
            )
        )

    def _get_mixin_rate_company(self):
        """
        Retorna la compañía relacionada (ej. self.company_id).
        """
        raise NotImplementedError(
            _(
                "Debe implementar el método '_get_mixin_rate_company' para obtener el tipo de cambio."
            )
        )

    def _get_mixin_rate_date(self):
        """
        Retorna la fecha de la operación (ej. self.date).
        """
        raise NotImplementedError(
            _(
                "Debe implementar el método '_get_mixin_rate_date' para obtener el tipo de cambio."
            )
        )

    # ---------------------------------------------------------------------------- #
    #                                TODO - METODOS                                #
    # ---------------------------------------------------------------------------- #
    def _get_forced_currency_rate(self):
        """
        Retorna la tasa de cambio forzada en formato invertido (1 / tasa), si aplica.

        La tasa forzada aplica solo si:
            - Se ha ingresado un valor positivo al campo forzar tipo de cambio (to_force_exchange_rate).
            - La moneda de la operación es distinta a la moneda base de la compañía.
        """
        self.ensure_one()

        from_currency = self._get_mixin_rate_company_currency()
        to_currency = self._get_mixin_rate_currency()

        if self.to_force_exchange_rate > 0.0 and from_currency != to_currency:
            return 1 / self.to_force_exchange_rate

        return None

    def _get_payment_currency_rate(self):
        """
        Calcula la tasa de cambio final a aplicar.

        Prioriza:
            - Tasa 1.0 si no hay conversión (monedas iguales).
            - El tipo de cambio forzado (si aplica).
            - Tipo de cambio estándar de Odoo si no hay forzado.
        """
        # Asegura que el método se ejecute sobre un único registro.
        self.ensure_one()

        # Obtiene la moneda base de la compañía.
        from_currency = self._get_mixin_rate_company_currency()
        # Obtiene la moneda de la operación.
        to_currency = self._get_mixin_rate_currency()
        # Obtiene el registro de la compañía.
        company = self._get_mixin_rate_company()
        # Obtiene la fecha de la operación.
        date = self._get_mixin_rate_date()

        # Si no hay moneda destino definida, se asume tasa neutra (1.0).
        # Validar que ambas monedas existan
        if not from_currency or not to_currency:
            return 1.0 

        # Si ambas monedas son iguales, no se requiere conversión.
        if from_currency == to_currency:
            return 1.0

        # Verifica si hay un tipo de cambio forzado válido.
        forced_rate = self._get_forced_currency_rate()
        if forced_rate is not None:
            # Usa la tasa forzada si aplica.
            return forced_rate

        # Obtiene la tasa de cambio desde Odoo según la fecha y la compañía.
        rate = self.env["res.currency"]._get_conversion_rate(
            # Moneda de origen.
            from_currency=from_currency,
            # Moneda de destino.
            to_currency=to_currency,
            # Compañía responsable.
            company=company,
            # Fecha de la operación.
            date=date or fields.Date.context_today(self),
        )

        # Odoo trabaja con tasas inversas, Si no hay una tasa válida, retorna 1.0 por seguridad.
        return 1 / rate if rate else 1.0

    # ---------------------------------------------------------------------------- #
    #                            TODO - METODOS ONCHANGE                           #
    # ---------------------------------------------------------------------------- #
    @api.onchange("to_force_exchange_rate")
    def _onchange_to_force_exchange_rate(self):
        """
        Limpia el tipo de cambio forzado si no se requiere.
        Si el tipo de cambio actual es 1 (es decir, no hay conversión real),
        se resetea `to_force_exchange_rate` a 0.0 para evitar inconsistencias.
        """
        from_currency = self._get_mixin_rate_company_currency()
        to_currency = self._get_mixin_rate_currency()

        if from_currency == to_currency:
            self.to_force_exchange_rate = 0.0

    # ---------------------------------------------------------------------------- #
    #                            TODO - METODOS COMPUTE                            #
    # ---------------------------------------------------------------------------- #
    @api.depends(
        lambda self: ["to_force_exchange_rate"] + self._get_mixin_rate_dependencies()
    )
    def _compute_exchange_rate(self):
        """
        Calcula y asigna el tipo de cambio al campo `exchange_rate`.
        """
        for record in self:
            record.exchange_rate = record._get_payment_currency_rate()
