from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta


READONLY_FIELD_STATES = {
    state: [("readonly", True)] for state in {"terminate", "cancel"}
}


class AccountRetention(models.Model):
    _name = "account.retention"
    _description = "Comprobante de retención"
    _check_company_auto = True
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name DESC, date_voucher DESC"

    state = fields.Selection(
        selection=[
            ("draft", "Borrador"),
            ("terminate", "Terminado"),
            ("cancel", "Cancelado"),
        ],
        string="Estado",
        readonly=True,
        tracking=True,
        index=True,
        default="draft",
        help="Estado del comprobante de retención.",
    )

    name = fields.Char(
        string="Nro. Retención",
        required=True,
        readonly=True,
        store=True,
        copy=False,
        tracking=True,
        default=lambda self: _("/"),
        index="trigram",
        help="Número único asignado al comprobante de retención.",
    )

    # ---------------------------------------------------------------------------- #
    #                                TODO - METODOS                                #
    # ---------------------------------------------------------------------------- #
    def get_usd_currency_rates(self):
        """
        Obtiene las tasas de cambio asociadas con la moneda USD (Dólar estadounidense).
        Si la moneda USD no está activa en la compañía, genera un mensaje de advertencia.

        Retorna:
            Recordset: Un recordset de las tasas de cambio para USD.
            Si no se encuentra o no está activa la moneda, lanza una excepción.
        """
        try:
            # Buscar la moneda USD (Dólar estadounidense)
            usd_currency = self.env["res.currency"].search(
                [("name", "=", "USD")], limit=1
            )

            # Verificar si la moneda USD está activa en la compañía actual
            company = self.env.company
            if not usd_currency:
                raise ValidationError(
                    _(
                        "La moneda USD (Dólar estadounidense) no está activa para la compañía '%s'."
                    )
                    % company.name
                )

            # Retornar las tasas de cambio asociadas a la moneda USD
            return usd_currency.rate_ids

        except Exception as e:
            raise ValidationError(
                _("Error al obtener las tasas de cambio para USD: %s") % str(e)
            )

    def _get_inverse_company_rate(self, rate_ids, date_retention=None):
        """
        Calcula la tasa inversa de la compañía basada en las tasas de cambio proporcionadas.
        Si no se encuentra la tasa para la fecha especificada, se intenta buscar la tasa
        para el día anterior. Si no se encuentra, se lanza un mensaje de error.

        Args:
            rate_ids (RecordSet): Conjunto de registros de tasas de cambio.
            date_retention (str): Fecha del comprobante en formato 'YYYY-MM-DD'. Si no se proporciona, se utiliza la fecha actual.
        """
        # Usar la fecha proporcionada o la fecha actual
        date_to_use = (
            fields.Date.from_string(date_retention)
            if date_retention
            else fields.Date.context_today(self)
        )

        # Filtrar la tasa correspondiente a la fecha especificada
        matching_rate = rate_ids.filtered(lambda r: r.name == date_to_use)

        # Si no se encuentra la tasa, buscar la tasa del día anterior
        if not matching_rate:
            previous_day = date_to_use - timedelta(days=1)
            matching_rate = rate_ids.filtered(lambda r: r.name == previous_day)

        # Si aún no se encuentra la tasa, lanzar un error con un mensaje claro
        if not matching_rate:
            raise ValidationError(
                _("No se encontró una tasa inversa para la fecha %s ni para el día %s.")
                % (
                    fields.Date.to_string(date_to_use),
                    fields.Date.to_string(previous_day),
                )
            )

        # Retornar la tasa inversa
        return matching_rate.inverse_company_rate

    def _get_related_account_move(self, account_move_id):
        """
        Busca el asiento contable relacionado con la retención por su ID.

        :param account_move_id: ID del asiento contable relacionado.
        :return: Registro de account.move relacionado o None si no se encuentra.
        """
        if account_move_id:
            return self.env["account.move"].browse(account_move_id.id).exists()
        return None

    def _get_account_payable(self, line_ids):
        """
        Filtra las líneas de la factura para obtener la cuenta por pagar.
        Asigna la primera cuenta encontrada o deja el campo vacío si no se encuentra ninguna.
        """
        # Filtrar líneas que correspondan a cuentas de tipo 'liability_payable'
        account_payable = line_ids.filtered(
            lambda line: line.account_id.account_type == "liability_payable"
        ).mapped("account_id")

        # Retornar la primera cuenta encontrada o False si no existe
        return account_payable[0] if account_payable else False

    def _prepare_move_lines(self):
        """
        Prepara y crea las líneas de asientos contables relacionadas con las retenciones.
        Si no existe un asiento contable, lo crea. Si ya existe, elimina las líneas anteriores y genera nuevas.
        """
        try:
            # Asignación de variables clave para mejorar la legibilidad
            name = self.name
            date_retention = self.date_retention
            journal_id = self.journal_id.id
            document_type_id = self.document_type_id.id
            partner_id = self.partner_id.id

            # Verificar si ya existe un asiento contable
            account_move_record = self.account_move_id

            if not account_move_record:
                # Crear un nuevo asiento contable si no existe
                account_move_record = self.env["account.move"].create(
                    {
                        "name": name,
                        "ref": "",
                        "date": date_retention,
                        "journal_id": journal_id,
                        "l10n_latam_document_type_id": document_type_id,
                    }
                )
            else:
                # Verificar que el asiento contable relacionado exista
                account_move_record = self._get_related_account_move(
                    account_move_record
                )
                if not account_move_record:
                    raise ValidationError(
                        _("No se encontró un asiento contable con ID %s.")
                        % self.account_move_id.id
                    )

                # Eliminar las líneas contables existentes antes de crear nuevas
                account_move_record.line_ids.unlink()

            move_lines = []

            # Preparar las líneas de apuntes contables (Débito y Crédito)
            for line in self.retention_line_ids:
                supplier_invoice = line.invoice_id
                amount_total_converted = line.amount_total_converted

                # Obtener la cuenta por pagar (liability_payable) de la factura
                account_payable = self._get_account_payable(supplier_invoice.line_ids)

                # Verificar si existe una cuenta por pagar válida
                if not account_payable:
                    raise ValidationError(
                        _("No se encontró una cuenta por pagar válida.")
                    )

                # Preparar los montos y monedas según la configuración de la línea
                amount_currency = line.amount_rt_base
                amount_retention = line.amount_rt
                currency_id = supplier_invoice.currency_id

                # Añadir las líneas de débito y crédito
                move_lines.extend(
                    [
                        # Línea de Débito
                        {
                            "move_id": account_move_record.id,
                            "supplier_invoice_id": supplier_invoice.id,
                            "amount_total_converted": amount_total_converted,
                            "account_id": account_payable.id,
                            "partner_id": partner_id,
                            "ref": supplier_invoice.name,
                            "name": name,
                            "amount_currency": amount_currency,
                            "currency_id": currency_id.id,
                            "debit": amount_retention,
                            "credit": 0,
                        },
                        # Línea de Crédito
                        {
                            "move_id": account_move_record.id,
                            "supplier_invoice_id": supplier_invoice.id,
                            "amount_total_converted": amount_total_converted,
                            "account_id": self.account_id.id,
                            "partner_id": partner_id,
                            "ref": supplier_invoice.name,
                            "name": name,
                            "amount_currency": -amount_retention,
                            "currency_id": self.company_currency_id.id,
                            "debit": 0,
                            "credit": amount_retention,
                        },
                    ]
                )

            # Crear todas las líneas contables en una sola operación
            self.env["account.move.line"].create(move_lines)

            # Asignar el ID del asiento contable creado/modificado
            self.account_move_id = account_move_record.id

        except ValidationError as e:
            # Re-lanzar excepciones de validación para mantener los mensajes originales
            raise e
        except Exception as e:
            # Capturar cualquier otra excepción y lanzar un error más descriptivo
            raise ValidationError(_("Error al generar apuntes contables: %s") % str(e))

    # ---------------------------------------------------------------------------- #
    #                             TODO - METODO CREATE                             #
    # ---------------------------------------------------------------------------- #
    @api.model
    def create(self, vals):
        """
        Sobrescribe el método `create` para:
        - Calcular y establecer la tasa de cambio inversa de la compañía, si aplica.
        - Generar y asignar el nombre del documento si es necesario.

        Parámetros:
            vals (dict): Diccionario de valores que se usarán para crear el registro.

        Retorna:
            record: El registro creado.
        """
        try:
            # Obtiene la fecha del comprobante del diccionario 'vals'
            date_retention = vals.get("date_retention")

            # Genera el nombre del documento si es necesario
            if vals.get("name", "/") == "/":
                # Obtiene las tasas de cambio para USD
                rate_ids = self.get_usd_currency_rates()

                if rate_ids:
                    # Calcula la tasa de cambio inversa utilizando la fecha del comprobante
                    inverse_company_rate = self._get_inverse_company_rate(
                        rate_ids, date_retention
                    )

                    # Asigna la tasa de cambio inversa al diccionario 'vals'
                    vals["inverse_company_rate"] = inverse_company_rate
                else:
                    # Asigna la tasa de cambio por default
                    vals["inverse_company_rate"] = 1

            # Crea el registro utilizando el método 'super' con los valores procesados
            return super(AccountRetention, self).create(vals)

        except ValidationError as ve:
            # Relanza errores de validación si ya existen
            raise ve
        except Exception as e:
            # Captura cualquier otra excepción y lanza un ValidationError con detalles
            raise ValidationError(
                _("Error al crear el registro de retención: %s") % str(e)
            )

    def unlink(self):
        """
        Elimina el registro de retención si se cumplen las condiciones necesarias.
        - No se permite la eliminación si el estado es 'Terminado'.
        - Si existe un asiento contable relacionado, desvincula el campo y elimina las líneas y el asiento.
        """
        for record in self:
            # Verifica si el registro está en estado 'Terminado', lo que impide su eliminación
            if record.state == "terminate":
                raise UserError(
                    _(
                        "No se puede eliminar el registro '%s' (ID: %s) porque está en estado 'Terminado'. "
                        "Cambie el estado a 'Borrador' para permitir la eliminación."
                    )
                    % (record.name or "", record.id)
                )

            # Obtener el asiento contable relacionado, si existe
            account_move_record = record._get_related_account_move(
                record.account_move_id
            )

            if account_move_record:
                # Desvincular el campo 'account_move_id' para romper la restricción de clave foránea
                record.account_move_id = False

                # Eliminar las líneas de apuntes contables existentes
                account_move_record.line_ids.unlink()

                # Eliminar el asiento contable
                account_move_record.unlink()

            # Eliminar las líneas de retención relacionadas
            record.retention_line_ids.unlink()

        # Llama al método unlink de la clase padre para completar la eliminación
        return super(AccountRetention, self).unlink()

    # ---------------------------------------------------------------------------- #
    #                              TODO - ACCION BOTON                             #
    # ---------------------------------------------------------------------------- #
    def action_post(self):
        """
        Cambia el estado de la retención a 'terminate' y publica el asiento contable relacionado, si aplica.
        Lanza una excepción si no se encuentra el asiento contable o si ocurre un error al publicarlo.
        """
        for record in self:
            # Buscar el asiento contable relacionado con la retención
            account_move_record = self._get_related_account_move(record.account_move_id)

            # Verificar si existe el asiento contable antes de proceder
            if not account_move_record:
                raise ValidationError(
                    _(
                        "No se encontró el asiento contable relacionado para la retención '%s'."
                    )
                    % record.name
                )

            try:
                # Cambiar el estado de la retención a 'terminate'
                record.write({"state": "terminate"})

                # Publicar el asiento contable relacionado
                account_move_record.action_post()
            except ValidationError as e:
                # Re-lanzar excepciones de validación para mantener los mensajes originales
                raise e
            except Exception as e:
                # Capturar cualquier otra excepción y lanzar un error más descriptivo
                raise ValidationError(
                    _("Error al publicar el asiento contable relacionado: %s") % str(e)
                )

    def button_draft(self):
        """
        Cambia el estado de la retención a 'draft' y el estado del asiento contable relacionado a 'draft' si existe.
        Maneja múltiples registros y lanza una excepción si ocurre un error al cambiar el estado del asiento contable.
        """
        for record in self:
            # Verificar si existen líneas de retención conflictivas
            conflicting_lines = self.env["account.retention.line"].search(
                [
                    (
                        "invoice_id",
                        "in",
                        record.retention_line_ids.mapped("invoice_id").ids,
                    ),
                    ("state", "!=", "cancel"),
                    ("retention_id", "!=", record.id),
                ],
            )

            if conflicting_lines:
                # Obtener los nombres de las facturas y comprobantes de retención en conflicto
                invoice_names = ", ".join(conflicting_lines.mapped("invoice_id.name"))
                retention_names = ", ".join(
                    conflicting_lines.mapped("retention_id.name")
                )

                raise ValidationError(
                    _(
                        "Las siguientes facturas: %s ya están asignadas a los siguientes comprobantes de retención "
                        "con estado diferente a 'Cancelado': %s."
                    )
                    % (invoice_names, retention_names)
                )

            # Obtener el asiento contable relacionado con la retención actual
            account_move_record = self._get_related_account_move(record.account_move_id)

            if account_move_record:
                try:
                    # Cambiar el estado del asiento contable relacionado a 'draft'
                    account_move_record.button_draft()
                except Exception as e:
                    raise ValidationError(
                        _(
                            "Error al cambiar el estado del asiento contable relacionado a 'borrador' para la retención '%s': %s"
                        )
                        % (record.name, str(e))
                    )

            # Cambiar el estado de la retención a 'draft'
            record.write({"state": "draft"})

    def button_cancel(self):
        """
        Cambia el estado de la retención a 'cancel' y establece el asiento contable relacionado a 'draft' si aplica.
        Maneja múltiples registros de manera independiente y asegura el manejo adecuado de errores.
        """
        for record in self:
            # Obtener el asiento contable relacionado al registro actual
            account_move_record = self._get_related_account_move(record.account_move_id)

            if account_move_record:
                try:
                    # Cambiar el estado del asiento contable relacionado a 'cancelado'
                    account_move_record.button_cancel()
                except Exception as e:
                    raise ValidationError(
                        _(
                            "Error al cambiar el estado del asiento contable relacionado a 'cancelado' para la retención '%s': %s"
                        )
                        % (record.name, str(e))
                    )

            # Cambiar el estado de la retención a 'cancel'
            record.write({"state": "cancel"})

    def set_terminate(self):
        """
        Cambia el estado a 'terminate' y crea los asientos contables correspondientes
        si el monto total convertido cumple con el mínimo requerido para la retención.
        """
        for record in self:
            # Verificar si el monto total convertido cumple con el mínimo requerido para la retención
            if record.amount_total_converted > record.amount_minimum_retention:
                # Preparar y crear las líneas contables
                record._prepare_move_lines()

                # Publicar el asiento contable relacionado
                record.action_post()

                # Cambiar el estado de la retención a 'terminate'
                record.write({"state": "terminate"})
            else:
                # Lanzar error si el monto convertido no cumple con el mínimo requerido
                raise ValidationError(
                    _(
                        "Error: El total convertido del comprobante '%s' debe ser mayor o igual al monto mínimo de "
                        "retención establecido por ley (%.2f)."
                    )
                    % (record.name, record.amount_minimum_retention)
                )

    def open_related_account_move(self):
        """
        Abre la vista del asiento contable relacionado.

        Este método verifica si existe un asiento contable asociado (account_move_id)
        y luego abre la vista del formulario correspondiente. Si no existe, se lanza un error.
        """
        # Verificar si existe el asiento contable relacionado
        if not self.account_move_id:
            raise UserError(
                _("No hay un asiento contable relacionado con este registro.")
            )

        # Preparar la acción para abrir la vista del asiento contable
        return {
            "type": "ir.actions.act_window",
            "name": _("Asiento Contable"),
            "res_model": "account.move",  # Modelo del asiento contable
            "view_mode": "form",  # Modo de vista: formulario
            "res_id": self.account_move_id.id,  # ID del registro de asiento a abrir
            "target": "current",  # Abrir en la misma ventana
            "context": dict(self.env.context),  # Pasar el contexto actual
        }
