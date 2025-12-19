from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError

# Definir una constante global para los dígitos en porcentaje
PERCENTAGE_DIGITS = (5, 2)


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    # Acción a realizar en el comprobante de retención
    action_retention = fields.Selection(
        selection=[
            ("generate", "Generar Comprobante"),
            ("attach", "Adjuntar a Comprobante"),
        ],
        string="Acción Comprobante de Retención",
        default="generate",
        required=True,
        help="Selecciona si deseas generar un nuevo comprobante o adjuntar este pago a uno existente en borrador.",
    )

    # Estado que indica si el comprobante de retención se publicará o quedará en borrador
    state = fields.Selection(
        selection=[
            ("draft", "Borrador"),
            ("published", "Publicado"),
        ],
        string="Estado",
        default="draft",
        required=True,
        help="Indica si el comprobante de retención será publicado o permanecerá en borrador.",
    )

    # Correlativo de comprobante al generar uno nuevo
    retention_sequence = fields.Char(
        string="Correlativo de Comprobante",
        help="Muestra y permite editar el correlativo del comprobante de retención cuando se elige 'Generar Comprobante'.",
    )

    # Selección de comprobante de retención en estado borrador para adjuntar el pago
    retention_id = fields.Many2one(
        comodel_name="account.retention",
        string="Comprobante de Retención",
        domain="[('state', '=', 'draft'), ('partner_id', '=', partner_id)]",
        help="Selecciona un comprobante en borrador para adjuntar el pago cuando se elige la opción 'Adjuntar a Comprobante'.",
    )

    # Indicador de si el socio es agente de retención fiscal
    is_retention_agent = fields.Boolean(
        string="Agente de Retención",
        default=False,
        help="Determina si el socio está autorizado como agente de retención fiscal según la normativa vigente.",
    )

    # Indica si se aplicará retención en este pago
    has_retention = fields.Boolean(
        string="¿Aplicar Retención?",
        default=False,
        help="Especifica si se aplicará retención al importe total de este pago.",
    )

    # Importe total del documento en la moneda del documento
    amount_total = fields.Monetary(
        string="Importe Total",
        currency_field="currency_id",
        compute="_compute_payment_and_total_amounts",
        store=True,
        readonly=True,
        help="Monto total del documento, calculado automáticamente y reflejando ajustes o reversiones.",
    )

    # Monto pagado hasta la fecha
    amount_paid = fields.Monetary(
        string="Importe Pagado",
        currency_field="currency_id",
        compute="_compute_payment_and_total_amounts",
        store=True,
        readonly=True,
        help="Monto total pagado hasta la fecha, actualizado automáticamente con cada pago registrado.",
    )

    # Porcentaje del monto total ya pagado
    percentage_paid = fields.Float(
        string="Porcentaje Pagado",
        compute="_compute_percentage_paid",
        store=True,
        readonly=True,
        digits=PERCENTAGE_DIGITS,  # Usa la constante global para precisión
        help="Porcentaje del monto total pagado, calculado en base a los pagos y retenciones registrados.",
    )

    # Porcentaje restante del monto total por pagar, editable para ajustes
    percentage_remaining = fields.Float(
        string="Porcentaje Restante por Pagar",
        compute="_compute_percentage_remaining",
        store=True,
        readonly=False,
        digits=PERCENTAGE_DIGITS,
        help="Porcentaje restante del monto total por pagar, editable para ajustes manuales si es necesario.",
    )

    # Importe retenido, calculado en base al porcentaje aplicable
    amount_retention = fields.Monetary(
        string="Importe Retenido",
        compute="_compute_retention_amounts",
        store=True,
        readonly=True,
        currency_field="currency_id",
        help="Monto retenido calculado en base al porcentaje de retención aplicable.",
    )

    # Porcentaje aplicable de retención sobre el monto imponible
    percentage_retention = fields.Float(
        string="Porcentaje de Retención",
        default=0.0,
        digits=PERCENTAGE_DIGITS,
        help="Porcentaje de retención aplicable sobre el monto imponible del documento.",
    )

    # Cuenta contable para registrar pagos, filtrada por compañía
    account_payable_id = fields.Many2one(
        comodel_name="account.account",
        string="Cuenta por Pagar",
        domain="[('company_id', '=?', company_id), ('deprecated', '=', False)]",
        help="Cuenta para registrar obligaciones de pago del documento, filtrada por la compañía actual.",
    )

    # Cuenta contable para registrar retenciones aplicadas
    account_retention_id = fields.Many2one(
        comodel_name="account.account",
        string="Cuenta de Retención",
        domain="[('company_id', '=?', company_id), ('deprecated', '=', False)]",
        help="Cuenta específica para registrar retenciones aplicadas en pagos, filtrada por la compañía actual.",
    )

    # ---------------------------------------------------------------------------- #
    #                               TODO - CONSTANTE                               #
    # ---------------------------------------------------------------------------- #
    # Constante para el cálculo de porcentajes
    PERCENTAGE_FACTOR = 100.0
    # Constante para el cantidad de digitos
    DIGITS = 8

    # ---------------------------------------------------------------------------- #
    #                                TODO - METODOS                                #
    # ---------------------------------------------------------------------------- #
    def _generate_correlative_name(self, prefix, series, sequence, digits):
        """
        Genera el nombre correlativo basado en el prefijo, la serie y la secuencia
        con la cantidad de dígitos especificados.

        :param prefix       : Prefijo definido en el tipo de documento.
        :param series       : Serie de retención asignada a la compañía.
        :param sequence     : Número secuencial del documento.
        :param digits       : Número de dígitos que debe tener la secuencia.
        :return             : Nombre correlativo completo.
        """
        # Validación de entradas
        if not prefix or not series or not sequence.isdigit():
            raise ValidationError(
                "El prefijo, la serie y la secuencia deben ser válidos y no estar vacíos."
            )

        # Formateo de la secuencia con ceros a la izquierda según los dígitos especificados
        formatted_sequence = str(int(sequence)).zfill(digits)

        # Construcción y retorno del nombre correlativo en el formato 'PREFIJO-SERIE-SECUENCIA'
        return f"{prefix}{series}-{formatted_sequence}"

    def _reset_retention_fields(self):
        """
        Restablece todos los campos relacionados con la retención a sus valores por defecto.
        Este método se utiliza para limpiar cualquier configuración previa de retención,
        """
        # Desmarcar el socio como agente de retención
        self.is_retention_agent = False

        # Eliminar la indicación de que el movimiento tiene retención aplicada
        self.has_retention = False

        # Restablecer el porcentaje de retención a 0
        self.percentage_retention = 0.0

        # Limpiar las cuentas contables relacionadas con la retención y cuentas por pagar
        self.account_payable_id = False
        self.account_retention_id = False

    def _get_account_payable(self, line_ids):
        """
        Obtiene la cuenta contable por pagar de las líneas de la factura.
        Filtra las líneas de factura en función de su tipo de cuenta y retorna la primera cuenta de 'liability_payable' encontrada.

        :param line_ids     : Registros de las líneas de la factura (account.move.line)
        :return             : El registro de la cuenta contable (account.account) de tipo 'liability_payable', o False si no se encuentra ninguna.
        """
        # Filtrar las líneas que correspondan a cuentas de tipo 'liability_payable'
        account_payable = line_ids.filtered(
            lambda line: line.account_id.account_type == "liability_payable"
        ).mapped("account_id")

        # Retorna la primera cuenta encontrada o False si no existe ninguna
        return account_payable[0] if account_payable else False

    def _calculate_retention_amount(self, percentage, amount):
        """
        Calcula el monto de retención basado en el monto y el porcentaje proporcionados.

        :param percentage   : Porcentaje de retención.
        :param amount       : Monto sobre el cual se calcula la retención.
        :return             : Monto de retención calculado.
        """
        if amount < 0:
            raise UserError("El monto no puede ser negativo.")

        # Calcula el monto de retención
        retention_amount = (percentage * amount) / self.PERCENTAGE_FACTOR

        # Redondea a dos decimales
        rounded_retention_amount = round(retention_amount, 2)

        return rounded_retention_amount

    def _calculate_amount_based_on_reversal(self, invoice):
        """
        Calcula el monto neto de una factura teniendo en cuenta todas las facturas revertidas publicadas.
        Si hay una o más facturas revertidas asociadas y publicadas, se ajusta el monto total de la factura original
        restando la suma de los montos de todas las facturas revertidas.

        :param invoice  : La factura original para la cual se calculará el monto ajustado.
        :return         : Monto ajustado de la factura.
        """
        try:
            # Validar que se reciba una factura
            if not invoice:
                return 0.0

            # Definir el dominio para encontrar las facturas revertidas asociadas y publicadas
            refund_domain = [
                # Tipo de movimiento debe ser reembolso
                ("move_type", "=", "in_refund"),
                # Facturas revertidas asociadas a la factura original
                ("reversed_entry_id", "=", invoice.id),
                # Solo considerar facturas publicadas
                ("state", "=", "posted"),
            ]

            # Buscar las facturas revertidas que cumplen con el dominio
            reversed_invoices = self.env["account.move"].search(refund_domain)

            # Calcular el monto total de las facturas revertidas
            total_refunded_amount = sum(reversed_invoices.mapped("amount_total"))

            # Calcular el monto ajustado restando los reembolsos del total de la factura original
            adjusted_amount = invoice.amount_total - total_refunded_amount

            rounded_adjusted_amount = round(adjusted_amount, 2)

            return rounded_adjusted_amount
        except Exception as e:
            # Captura y manejo de posibles errores, retorna 0.0 si ocurre algún fallo
            raise ValidationError(
                _("Error al calcular el Importe Total para la factura %s: %s")
                % (invoice.name or "Desconocida", str(e))
            )

    def _get_total_paid_amount(self, invoice):
        """
        Calcula el monto total pagado relacionado con una factura, incluyendo tanto los pagos realizados
        como las líneas de retención asociadas.

        :param invoice  : Registro de la factura para la cual se calcularán los pagos y retenciones.
        :return         : Monto total pagado, incluyendo retenciones, o 0.0 si la factura no es válida.
        """
        try:
            # Retornar 0.0 si la factura no es válida
            if not invoice:
                return 0.0

            # Dominio para buscar los pagos reconciliados y publicados relacionados con la factura
            payment_domain = [
                # Pagos relacionados con la factura
                ("reconciled_bill_ids", "in", [invoice.id]),
                # Tipo de socio proveedor
                ("partner_type", "=", "supplier"),
                # Excluir transferencias internas
                ("is_internal_transfer", "=", False),
                # Referencia coincidente con la factura
                ("ref", "!=", ""),
                ("ref", "in", [invoice.name, invoice.ref]),
                # Solo pagos publicados
                ("state", "=", "posted"),
            ]

            # Dominio para buscar las líneas de retención asociadas a la factura
            retention_domain = [
                # Relación con la factura
                ("invoice_id", "=", invoice.id),
                # Líneas de retención terminadas
                ("state", "=", "terminate"),
            ]

            # Buscar pagos relacionados con la factura
            payments = self.env["account.payment"].search(payment_domain)
            # Buscar líneas de retención asociadas
            retention_lines = self.env["account.retention.line"].search(
                retention_domain
            )

            # Sumar los montos de los pagos realizados
            total_payments = sum(payments.mapped("amount"))
            # Sumar los montos retenidos de las líneas de retención
            total_retention_amount = sum(retention_lines.mapped("amount_rt_base"))

            # Calcular el total pagado (pagos + retenciones)
            total_paid_amount = total_payments + total_retention_amount

            # Redondea a dos decimales
            rounded_total_paid_amount = round(total_paid_amount, 2)

            return rounded_total_paid_amount

        except Exception as e:
            # Manejar cualquier excepción y mostrar un mensaje claro al usuario
            raise ValidationError(
                _("Ocurrió un error al calcular los pagos de la factura '%s': %s")
                % (invoice.name or _("Desconocida"), str(e))
            )

    def _create_payment_vals_from_wizard(self, batch_result):
        """
        Sobrescribe el método para incluir los valores relacionados con la retención
        en el registro de pago si el socio es un agente de retención.
        """
        # Obtener los valores base del pago a partir del método padre
        payment_vals = super(
            AccountPaymentRegister, self
        )._create_payment_vals_from_wizard(batch_result)

        # Verificar si el socio es un agente de retención y tiene retención habilitada
        if self.is_retention_agent and self.has_retention:
            # Calcular el monto después de aplicar la retención
            amount_after_retention = round(self.amount - self.amount_retention, 2)

            # Actualizar los valores del pago con los datos relacionados a la retención
            payment_vals.update(
                {
                    "is_retention_agent": True,  # Indicar que el socio es agente de retención
                    "has_retention": True,  # Indicar que la retención está habilitada
                    "company_id": self.company_id.id,  # Compañía asociada al pago
                    "amount_base": self.amount,  # Monto original antes de aplicar la retención
                    "amount": amount_after_retention,  # Monto a pagar después de retención
                    "amount_retention": self.amount_retention,  # Monto retenido
                    "percentage_retention": self.percentage_retention,  # Porcentaje de retención aplicado
                    "amount_minimum_retention": self.company_id.amount_minimum_retention,  # Monto mínimo para retención
                    "journal_retention_id": self.company_id.journal_retention_id.id,  # Diario contable para la retención
                    "account_retention_id": self.company_id.account_retention_id.id,  # Cuenta contable para la retención
                    "document_type_retention_id": self.company_id.document_type_retention_id.id,  # Tipo de documento de retención
                }
            )

        return payment_vals

        # # Obtener la tasa de conversión entre la moneda del pago y la moneda de la compañía
        # conversion_rate = self.env["res.currency"]._get_conversion_rate(
        #     self.currency_id,
        #     self.company_id.currency_id,
        #     self.company_id,
        #     self.payment_date,
        # )

        # # Generar el nombre del registro contable para la retención
        # name = f"Retención: {self.communication}"

        # balance = self.company_id.currency_id.round(
        #     self.amount_retention * conversion_rate
        # )

        # # Agregar los valores de retención a las líneas de asiento contable
        # payment_vals["write_off_line_vals"].extend(
        #     [
        #         # Línea de Haber
        #         {
        #             "account_id": self.account_payable_id.id,
        #             "partner_id": self.partner_id.id,
        #             "name": name,
        #             "amount_currency": -self.amount_retention,
        #             "currency_id": self.company_currency_id.id,
        #             "balance": -balance,
        #         },
        #         # Línea de Debe
        #         {
        #             "account_id": self.account_retention_id.id,
        #             "partner_id": self.partner_id.id,
        #             "name": name,
        #             "amount_currency": self.amount_retention,
        #             "currency_id": self.currency_id.id,
        #             "balance": balance,
        #         },
        #     ]
        # )

    # ---------------------------------------------------------------------------- #
    #                            TODO - METODO ONCHANGE                            #
    # ---------------------------------------------------------------------------- #
    @api.onchange("company_id")
    def _onchange_company_id(self):
        """
        Actualiza el porcentaje de retención y las cuentas contables según la compañía seleccionada.
        Se aplica si el socio es un agente de retención y el tipo de movimiento es 'in_invoice' (factura de proveedor).
        """
        # Asegura que el método procese un único registro a la vez para evitar inconsistencias
        self.ensure_one()

        # Verifica las condiciones iniciales:
        # - Compañía está seleccionada
        # - Existen líneas en la factura
        # - El tipo de movimiento es 'in_invoice' (factura de proveedor)
        if (
            self.company_id
            and self.line_ids
            and self.line_ids[0].move_type == "in_invoice"
        ):
            # Actualiza los campos de retención basados en la información del movimiento asociado
            move = self.line_ids[0].move_id
            self.is_retention_agent = move.is_retention_agent
            self.has_retention = move.has_retention

            # Si el socio es un agente de retención y la compañía cambió
            if (
                self.is_retention_agent
                and self.has_retention
                and self.company_id != self._origin.company_id
            ):
                # Actualiza el porcentaje de retención basado en la compañía seleccionada
                self.percentage_retention = self.company_id.percentage_retention or 0.0

                # Obtiene la cuenta por pagar asociada a las líneas de la factura
                payable_account = self._get_account_payable(self.line_ids)
                self.account_payable_id = (
                    payable_account.id if payable_account else False
                )

                # Asigna la cuenta de retenciones de la compañía seleccionada
                self.account_retention_id = (
                    self.company_id.account_retention_id.id or False
                )
            else:
                # Si no es un agente de retención, restablece los campos relacionados
                self._reset_retention_fields()
        else:
            # Si no se cumplen las condiciones iniciales, restablece los campos
            self._reset_retention_fields()

    @api.onchange("amount_total", "percentage_remaining")
    def onchange_amount_based_on_percentage(self):
        """
        Actualiza el campo `amount` según el porcentaje restante modificado.
        Si el porcentaje está fuera de rango, lanza un error de validación.
        """
        if self.is_retention_agent and self.has_retention:
            # Asegurarse de que el porcentaje restante es válido y ha cambiado
            if self.percentage_remaining != self._origin.percentage_remaining:
                if 0 < self.percentage_remaining <= 100.0:
                    # Calcular el monto basado en el porcentaje restante
                    self.amount = self.amount_total * (
                        self.percentage_remaining / 100.0
                    )
                else:
                    # Lanzar error si el porcentaje está fuera del rango permitido
                    raise ValidationError(
                        _(
                            "El porcentaje restante debe ser mayor que 0 y no exceder 100.0%."
                        )
                    )

    @api.onchange("action_retention")
    def onchange_retention_sequence(self):
        """
        Actualiza el campo `retention_sequence` cada vez que cambia el valor de `action_retention`.
        Si la acción seleccionada es "generate", calcula y asigna el siguiente número de secuencia
        basado en el prefijo y la serie configurados para la compañía.
        """
        if self.action_retention == "generate":
            # Definir el número de dígitos para la secuencia de retención
            digits = self.DIGITS

            # Obtener el prefijo del tipo de documento y la serie del diario de retención configurados en la compañía
            prefix = self.company_id.document_type_retention_id.doc_code_prefix or ""
            series = self.company_id.journal_retention_id.code or ""

            # Determinar el siguiente número de secuencia basado en el último correlativo de retención
            last_sequence = (
                self.company_id.journal_retention_id.retention_sequence or ""
            )
            if last_sequence.isdigit():
                # Incrementa la secuencia y rellena con ceros a la izquierda según el tamaño especificado
                sequence = str(int(last_sequence) + 1).zfill(digits)
            else:
                # Usa el valor inicial "1" si no hay una secuencia previa válida
                sequence = str(1).zfill(digits)

            # Generar y asignar el nombre completo correlativo en el campo `retention_sequence`
            self.retention_sequence = self._generate_correlative_name(
                prefix, series, sequence, digits
            )
        else:
            # Restablece `retention_sequence` si la acción no es "generate"
            self.retention_sequence = False

    @api.onchange("action_retention")
    def onchange_retention_id(self):
        """
        Actualiza el campo `retention_id` en función de la acción de retención seleccionada.
        Si la acción es "attach", busca el primer documento de retención en estado "borrador"
        asociado con el proveedor actual. Si no se encuentra, establece `retention_id` en False.
        """
        if self.action_retention == "attach":
            # Buscar el primer documento de retención en estado "draft" para el proveedor actual
            self.retention_id = self.env["account.retention"].search(
                [("state", "=", "draft"), ("partner_id", "=", self.partner_id.id)],
                limit=1,
                order="name DESC",
            )
        else:
            # Restablece `retention_id` si la acción seleccionada no es "attach"
            self.retention_id = False

    # ---------------------------------------------------------------------------- #
    #                             TODO - METODO COMPUTE                            #
    # ---------------------------------------------------------------------------- #
    @api.depends("company_id", "line_ids")
    def _compute_payment_and_total_amounts(self):
        """
        Calcula el monto total y el monto pagado en función de la reversión y la información de las líneas,
        si el socio es un agente de retención. Se asegura de manejar correctamente los casos donde no hay líneas
        o cuando el socio no es un agente de retención.
        """
        for rec in self:
            # Inicializar los montos a 0 por defecto
            rec.amount_total = 0.0
            rec.amount_paid = 0.0

            # Solo proceder si el socio es un agente de retención
            if rec.is_retention_agent and rec.has_retention and rec.line_ids:
                # Obtener el movimiento asociado a las líneas de la factura
                move_id = rec.line_ids[0].move_id

                # Calcular el monto total, considerando si hay una reversión del documento
                rec.amount_total = self._calculate_amount_based_on_reversal(move_id)

                # Calcular el monto total pagado hasta la fecha
                rec.amount_paid = self._get_total_paid_amount(move_id)

    @api.depends("amount_total", "amount_paid")
    def _compute_percentage_paid(self):
        """
        Calcula el porcentaje del monto total que ha sido pagado. Si el monto total es mayor que 0,
        se divide el monto pagado entre el monto total para obtener el porcentaje pagado.
        Si el monto total es 0 o menor, el porcentaje pagado será 0.
        """
        for record in self:
            try:
                # Inicializar el porcentaje pagado a 0.0 por defecto
                record.percentage_paid = 0.0

                # Verificar si el agente tiene retención habilitada y el monto total es válido
                if (
                    record.is_retention_agent
                    and record.has_retention
                    and record.amount_total > 0
                ):
                    # Calcular el porcentaje pagado
                    record.percentage_paid = (
                        record.amount_paid / record.amount_total
                    ) * 100

            except Exception as error:
                # Capturar cualquier otra excepción inesperada
                raise ValidationError(
                    f"Ocurrió un error inesperado al calcular el porcentaje pagado: {error}"
                )

    @api.depends("amount", "percentage_retention")
    def _compute_retention_amounts(self):
        """
        Calcula los montos de retención aplicando el porcentaje de retención (`percentage_retention`)
        sobre el monto original (`amount`). El resultado se almacena en el campo `amount_retention`
        y se redondea a 2 decimales. Si el porcentaje de retención o el monto son inválidos,
        o si el socio no es un agente de retención, el monto retenido será 0.0.
        """
        for record in self:
            try:
                # Asignar 0.0 como valor predeterminado
                record.amount_retention = 0.0

                # Verificar si el socio es un agente de retención con retención habilitada y si los valores son válidos
                if (
                    record.is_retention_agent
                    and record.has_retention
                    and record.percentage_retention > 0
                    and record.amount > 0
                ):
                    # Calcular el monto retenido y redondear a 2 decimales
                    retention_amount = self._calculate_retention_amount(
                        record.percentage_retention, record.amount
                    )
                    record.amount_retention = round(retention_amount, 2)
            except Exception as error:
                # Captura cualquier otra excepción inesperada
                raise ValidationError(
                    f"Ocurrió un error inesperado al calcular los montos de retención: {error}"
                )

    @api.depends("amount_total", "amount")
    def _compute_percentage_remaining(self):
        """
        Calcula el porcentaje restante por pagar basado en el monto pendiente (`amount`) y el monto total (`amount_total`).
        Si el monto total es 0 o no válido, el porcentaje restante se establece en 0.
        """
        for record in self:
            try:
                # Inicializar el porcentaje restante a 0.0 por defecto
                record.percentage_remaining = 0.0

                # Verificar que el monto total sea mayor a 0 y que haya un monto pendiente
                if record.amount_total > 0 and record.amount > 0:
                    # Calcular el porcentaje restante y redondear a 2 decimales
                    record.percentage_remaining = (
                        record.amount / record.amount_total
                    ) * 100
            except Exception as error:
                # Capturar cualquier otra excepción inesperada
                raise ValidationError(
                    f"Ocurrió un error inesperado al calcular el porcentaje restante: {error}"
                )
