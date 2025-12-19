from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError


class AccountRetentionLine(models.Model):
    _name = "account.retention.line"
    _description = "Detalle de Comprobante de Retención"
    _check_company_auto = True
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Configuraciones para precisión de campos monetarios y flotantes
    _precision_digits_monetary = (16, 2)
    _precision_digits_float = (3, 2)

    def _get_account_move_state_selection(self):
        """Obtiene la selección de estados del campo 'move_type' del modelo 'account.move'."""
        return self.env["account.move"].fields_get(allfields=["move_type"])[
            "move_type"
        ]["selection"]

    name = fields.Char(
        string="Descripción",
        size=64,
        help="Descripción de la línea de retención. Ejemplo: retención de factura o servicio específico.",
    )

    retention_id = fields.Many2one(
        comodel_name="account.retention",
        string="Comprobante de Retención",
        ondelete="cascade",
        help="Comprobante de retención al que pertenece el registro. Usado para documentos emitidos en cumplimiento con la normativa peruana de retenciones.",
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Compañía",
        related="retention_id.company_id",
        store=True,
        readonly=True,
        help="Compañía a la que está asociada la retención.",
    )

    state = fields.Selection(
        string="Estado",
        related="retention_id.state",
        readonly=True,
        help="Estado actual del comprobante de retención: borrador, validado o cancelado.",
    )

    inverse_company_rate = fields.Float(
        string="Tipo de Cambio Inverso",
        digits="Product Price",
        default=1.000,
        related="retention_id.inverse_company_rate",
        readonly=True,
        help="Tipo de cambio inverso usado para convertir montos en la moneda de la compañía si es diferente a la moneda de la factura.",
    )

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Proveedor",
        related="retention_id.partner_id",
        store=True,
        readonly=True,
        help="Proveedor o entidad a la que se le aplica la retención según la normativa de SUNAT.",
    )

    invoice_id = fields.Many2one(
        comodel_name="account.move",
        string="Factura",
        required=True,
        domain="[('partner_id', '=', partner_id), ('move_type', '=', 'in_invoice'), ('state', 'not in', ['draft', 'cancel'])]",
        ondelete="restrict",
        index=True,
        auto_join=True,
        check_company=True,
        help="Factura o documento del proveedor sobre el cual se aplica la retención. Debe estar validado y no puede estar cancelado.",
    )

    invoice_date = fields.Date(
        string="Fecha Factura",
        compute="_compute_invoice_related_fields",
        store=True,
        help="Fecha de emisión de la factura en la que se emitió el documento asociado.",
    )

    type = fields.Selection(
        selection=_get_account_move_state_selection,
        string="Tipo de Factura",
        compute="_compute_invoice_related_fields",
        store=True,
        help="Indica el tipo de documento asociado a la retención o transacción.",
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda Factura",
        compute="_compute_invoice_related_fields",
        store=True,
        help="Moneda en la que fue emitida la factura sujeta a retención.",
    )

    amount_total = fields.Monetary(
        string="Total Factura",
        currency_field="currency_id",
        digits=_precision_digits_monetary,
        compute="_compute_invoice_related_fields",
        store=True,
        help="Monto total de la factura emitida por el proveedor en la moneda original.",
    )

    amount_paid = fields.Monetary(
        string="Total Pagado",
        digits=_precision_digits_monetary,
        currency_field="currency_id",
        store=True,
        help="Total pagado a la fecha sobre la factura sujeta a retención. Calculado automáticamente.",
    )

    percentage_paid = fields.Float(
        string="% Pagado",
        digits=_precision_digits_float,
        compute="_compute_percentage_paid",
        store=True,
        readonly=True,
        help="Porcentaje del monto total de la factura que ha sido pagado a la fecha.",
    )

    amount = fields.Monetary(
        string="Importe",
        digits=_precision_digits_monetary,
        currency_field="currency_id",
        store=True,
        help="Importe sobre el cual se aplicará la retención, expresado en la moneda de la factura.",
    )

    percentage_remaining = fields.Float(
        string="% Restante",
        digits=_precision_digits_float,
        compute="_compute_percentage_remaining",
        store=True,
        readonly=False,
        help="Porcentaje restante del importe que aún no ha sido pagado, ajustable si es necesario.",
    )

    amount_rt_base = fields.Monetary(
        string="Base Retención",
        digits=_precision_digits_monetary,
        compute="_compute_retention_amounts",
        store=True,
        readonly=True,
        help="Monto base para la retención, antes de aplicar cualquier tipo de conversión o tasa de cambio.",
        currency_field="currency_id",
    )

    company_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda de la Compañía",
        related="retention_id.company_currency_id",
        readonly=True,
        help="Moneda principal utilizada por la compañía para emitir la retención.",
    )

    oper_rate = fields.Float(
        string="Tipo de Cambio",
        digits="Product Price",
        default=1.0000,
        compute="_compute_oper_rate",
        store=True,
        readonly=True,
        help="Tipo de cambio aplicada para convertir entre la moneda de la factura y la moneda de la compañía. Se utiliza si ambas monedas son diferentes.",
    )

    percentage_retention = fields.Float(
        string="% Retención",
        digits=_precision_digits_float,
        related="retention_id.percentage_retention",
        store=True,
        readonly=True,
        help="Porcentaje de retención aplicado según la normativa vigente en Perú.",
    )

    # retention_base_amount = fields.Monetary(
    #     string="Retención Base",
    #     digits=_precision_digits_monetary,
    #     store=True,
    #     readonly=True,
    #     help="Monto retenido antes de aplicar la conversión, basado en el monto original.",
    #     currency_field="currency_id",
    # )

    amount_total_converted = fields.Monetary(
        string="Total Convertido",
        digits=_precision_digits_monetary,
        compute="_compute_converted_amounts",
        store=True,
        readonly=True,
        currency_field="company_currency_id",
        help="Monto total de la factura convertido a la moneda de la compañía usando la tasa de cambio aplicada.",
    )

    amount_converted = fields.Monetary(
        string="Importe Convertido",
        digits=_precision_digits_monetary,
        compute="_compute_converted_amounts",
        store=True,
        readonly=True,
        currency_field="company_currency_id",
        help="Importe total convertido a la moneda de la compañía, después de aplicar la retención.",
    )

    amount_rt = fields.Monetary(
        string="Retención Aplicada",
        digits=_precision_digits_monetary,
        compute="_compute_converted_amounts",
        store=True,
        readonly=True,
        currency_field="company_currency_id",
        help="Monto total retenido convertido a la moneda de la compañía, basado en las reglas de retención vigentes.",
    )

    # ---------------------------------------------------------------------------- #
    #                               TODO - CONSTANTE                               #
    # ---------------------------------------------------------------------------- #
    PERCENTAGE_FACTOR = 100.0  # Constante para el cálculo de porcentajes

    # ---------------------------------------------------------------------------- #
    #                           TODO - METODO CONSTRAINT                           #
    # ---------------------------------------------------------------------------- #
    @api.constrains("invoice_id", "state", "amount")
    def _check_unique_invoice(self):
        """
        Verifica que la factura (invoice_id) no esté asociada a líneas de retención
        activas cuyo monto total exceda el saldo restante de la factura.
        Si ya existen líneas en conflicto, lanza una excepción listando los comprobantes en cuestión.
        """
        for record in self:
            if record.state != "cancel":
                # Buscar todas las líneas de retención activas (no canceladas) para la misma factura
                existing_lines = self.search(
                    [
                        ("state", "!=", "cancel"),
                        ("invoice_id", "=", record.invoice_id.id),
                    ]
                )

                if existing_lines:
                    # Calcular el monto total de las líneas existentes
                    total_existing_amount = sum(existing_lines.mapped("amount"))

                    # Validar si el monto total de las líneas activas excede el monto total de la factura
                    if (
                        total_existing_amount > record.amount_total
                        or record.percentage_paid > 100.0
                    ):
                        # Filtrar las líneas existentes para excluir la línea actual en caso de actualización
                        filtered_lines = existing_lines.filtered(
                            lambda line: line.id != record.id
                        )

                        # Obtener los nombres de las retenciones asociadas a las líneas filtradas
                        retention_names = ", ".join(
                            filtered_lines.mapped("retention_id.name")
                        )

                        # Lanzar una excepción si el monto total de las líneas activas excede el monto total de la factura
                        if total_existing_amount > record.amount_total:
                            raise ValidationError(
                                _(
                                    "La factura '%s' ya está asignada a los siguientes comprobantes de retención "
                                    "que no están en estado 'Cancelado': %s. El monto total asignado supera el monto total de la factura."
                                )
                                % (record.invoice_id.name or "", retention_names)
                            )

    # ---------------------------------------------------------------------------- #
    #                                TODO - METODOS                                #
    # ---------------------------------------------------------------------------- #
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

    # ---------------------------------------------------------------------------- #
    #                            TODO - METODO ONCHANGE                            #
    # ---------------------------------------------------------------------------- #
    @api.onchange("amount_total", "percentage_remaining")
    def onchange_amount_based_on_percentage(self):
        """
        Actualiza el campo `amount` según el porcentaje restante modificado.
        Si el porcentaje está fuera de rango, lanza un error de validación.
        """
        # Verificar si el porcentaje ha cambiado y es válido
        if self.percentage_remaining != self._origin.percentage_remaining:
            if 0 < self.percentage_remaining <= 100.0:
                # Calcular el monto basado en el porcentaje restante
                self.amount = round(
                    self.amount_total * (self.percentage_remaining / 100.0), 2
                )
            else:
                # Lanzar error si el porcentaje está fuera del rango permitido
                raise ValidationError(
                    _(
                        "El porcentaje restante debe ser mayor que 0 y no exceder 100.0%."
                    )
                )

    @api.onchange("amount_total")
    def onchange_amount_based_on_total(self):
        """
        Actualiza 'amount' basado en 'amount_total'.
        Si la suma de 'amount_paid' y 'amount_rt_base' excede 'amount_total',
        lanza un error. Si no, actualiza 'amount'.
        """
        # Verifica que 'amount_total' sea mayor a 0 y haya cambiado
        if self.amount_total > 0 and self.amount_total != self._origin.amount_total:
            # Suma de montos pagados y retenidos
            total_calculated_amount = self.amount_paid + self.amount_rt_base

            # Lanza error si la suma excede el total
            if total_calculated_amount > self.amount_total:
                raise ValidationError(
                    f"La suma de pagado y retenido ({total_calculated_amount}) "
                    f"no puede exceder el monto total ({self.amount_total})."
                )
            else:
                self.amount = round(self.amount_total, 2)
        else:
            self.amount = 0.0

    @api.onchange("amount", "percentage_remaining")
    def onchange_amount_paid(self):
        """
        Actualiza el monto pagado y verifica que la retención no exceda el saldo de la factura.
        """
        # Obtener la factura relacionada
        related_invoice = self.invoice_id

        if related_invoice and self.amount > 0:
            # Calcular el monto total pagado
            self.amount_paid = self._get_total_paid_amount(related_invoice)

            # Calcular el monto restante a pagar
            total_remaining_amount = round(self.amount_paid + self.amount_rt_base, 2)

            # Verificar que la retención no exceda el saldo pendiente de la factura
            if total_remaining_amount > self.amount_total:
                raise ValidationError(
                    _("La retención '%s' no puede superar el importe adeudado '%s'.")
                    % (self.amount_rt_base, related_invoice.amount_residual)
                )

    # ---------------------------------------------------------------------------- #
    #                             TODO - METODO COMPUTE                            #
    # ---------------------------------------------------------------------------- #
    @api.depends("invoice_id")
    def _compute_invoice_related_fields(self):
        """
        Actualiza los campos relacionados con la factura seleccionada.
        Si no hay factura, los valores se restablecen.
        """
        for record in self:
            try:
                invoice = record.invoice_id
                if invoice:
                    # Calcula el monto total considerando reversiones
                    total_amount = self._calculate_amount_based_on_reversal(invoice)

                    # Obtiene el total pagado de la factura
                    total_paid = self._get_total_paid_amount(invoice)

                    # Actualiza los campos relacionados
                    record.update(
                        {
                            "invoice_date": invoice.invoice_date,
                            "type": invoice.move_type,
                            "currency_id": invoice.currency_id.id,
                            "amount_total": total_amount,
                            "amount_paid": total_paid,
                        }
                    )
                else:
                    # Restablece los campos si no hay factura
                    record.update(
                        {
                            "invoice_date": False,
                            "type": False,
                            "currency_id": False,
                            "amount_total": 0.0,
                            "amount_paid": 0.0,
                        }
                    )
            except Exception as error:
                raise ValidationError(
                    f"Error al actualizar los campos de la factura: {error}"
                )

    @api.depends("inverse_company_rate", "currency_id", "company_currency_id")
    def _compute_oper_rate(self):
        """
        Calcula la tasa de conversión (oper_rate) entre la moneda de la compañía
        y la moneda del documento. Usa `inverse_company_rate` si son diferentes.
        """
        for rec in self:
            # Tasa predeterminada es 1.0 si las monedas son iguales
            rec.oper_rate = 1.0000

            # Si las monedas son distintas, usa la tasa inversa
            if rec.company_currency_id != rec.currency_id:
                rec.oper_rate = rec.inverse_company_rate

    @api.depends("amount_total", "amount", "oper_rate")
    def _compute_converted_amounts(self):
        """
        Calcula los montos convertidos a la moneda de la compañía utilizando la tasa de conversión `oper_rate`.
        Se asegura de que la tasa de conversión sea válida antes de realizar los cálculos y redondea los resultados
        a 2 decimales para mayor precisión.
        """
        for record in self:
            try:
                if record.oper_rate > 0:
                    # Calcular y redondear el monto total convertido
                    record.amount_total_converted = round(
                        record.amount_total * record.oper_rate, 2
                    )

                    # Calcular y redondear el monto convertido basado en el campo 'amount'
                    record.amount_converted = round(record.amount * record.oper_rate, 2)

                    # Calcular y redondear el monto retenido convertido basado en 'amount_rt_base'
                    record.amount_rt = round(
                        record.amount_rt_base * record.oper_rate, 2
                    )
                else:
                    # Si no hay tasa de conversión válida, se asigna 0.0 a los montos convertidos
                    record.amount_total_converted = 0.0
                    record.amount_converted = 0.0
                    record.amount_rt = 0.0
            except Exception as error:
                raise ValidationError(
                    f"Error al calcular los montos convertidos: {error}"
                )

    @api.depends("percentage_retention", "amount")
    def _compute_retention_amounts(self):
        """
        Calcula los montos de retención aplicando el porcentaje de retención (`percentage_retention`)
        sobre el monto original (`amount`). El resultado se almacena en el campo `amount_rt_base` y se redondea a 2 decimales.
        Si no se especifica un porcentaje de retención, el monto retenido será 0.0.
        """
        for record in self:
            try:
                # Verificar si se ha definido un porcentaje de retención
                if record.percentage_retention:
                    # Calcular el monto retenido y redondear a 2 decimales
                    record.amount_rt_base = round(
                        self._calculate_retention_amount(
                            record.percentage_retention, record.amount
                        ),
                        2,
                    )
                else:
                    # Si no hay porcentaje de retención, asignar 0.0
                    record.amount_rt_base = 0.0
            except Exception as error:
                raise ValidationError(
                    f"Ocurrió un error inesperado al calcular los montos de retención: {error}"
                )

    @api.depends("amount_total", "amount_paid")
    def _compute_percentage_paid(self):
        """
        Calcula el porcentaje pagado basado en el monto total (`amount_total`) y el monto pagado (`amount_paid`).
        Si no hay un monto total o este es 0, el porcentaje pagado se establece en 0.
        """
        for record in self:
            try:
                if record.amount_total > 0:
                    # Calcula el porcentaje pagado si hay un monto total válido
                    record.percentage_paid = (
                        record.amount_paid / record.amount_total
                    ) * 100
                else:
                    # Si no hay monto total, el porcentaje pagado es 0
                    record.percentage_paid = 0.0
            except Exception as error:
                raise ValidationError(
                    f"Ocurrió un error inesperado al calcular el porcentaje pagado: {error}"
                )

    @api.depends("amount_total", "amount")
    def _compute_percentage_remaining(self):
        """
        Calcula el porcentaje restante por pagar basado en el monto pendiente (`amount`) y el monto total (`amount_total`).
        Si el monto total es 0 o no válido, el porcentaje restante se establece en 0.
        """
        for record in self:
            try:
                if record.amount_total > 0:
                    # Calcula el porcentaje restante si el monto total es válido
                    record.percentage_remaining = (
                        record.amount / record.amount_total
                    ) * 100
                else:
                    # Si el monto total no es válido, el porcentaje restante es 0
                    record.percentage_remaining = 0.0
            except Exception as error:
                raise ValidationError(f"Error al calcular el porcentaje: {error}")
