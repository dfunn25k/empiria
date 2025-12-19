from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError

READONLY_FIELD_STATES = {state: [("readonly", True)] for state in {"posted", "cancel"}}


class AccountPayment(models.Model):
    _inherit = "account.payment"

    retention_id = fields.Many2one(
        comodel_name="account.retention",
        string="Comprobante de Retención",
        ondelete="set null",
        help="Referencia al comprobante de retención asociado a esta línea. Cuando se elimina el comprobante de retención, este campo se establecerá en null en lugar de eliminar la línea actual.",
    )

    is_retention_agent = fields.Boolean(
        string="¿Es Agente de Retención?",
        readonly=False,
        store=True,
        tracking=True,
        compute="_compute_is_retention_agent",
        states=READONLY_FIELD_STATES,
        help="Indica si el socio asociado es un agente de retención autorizado por la ley.",
    )

    has_retention = fields.Boolean(
        string="¿Pago con Retención?",
        store=True,
        default=False,
        tracking=True,
        states=READONLY_FIELD_STATES,
        help="Indica si el pago asociado tendrá una retención aplicada.",
    )

    amount_base = fields.Monetary(
        string="Importe Base",
        store=True,
        currency_field="currency_id",
        states=READONLY_FIELD_STATES,
        help="",
    )

    amount_retention = fields.Monetary(
        string="Importe Retenido",
        compute="_compute_amount_retention",
        store=True,
        readonly=True,
        tracking=True,
        currency_field="currency_id",
        help="Monto base sujeto a retención, calculado en base al porcentaje de retención.",
    )

    percentage_retention = fields.Float(
        string="Porcentaje de Retención (%)",
        store=True,
        tracking=True,
        states=READONLY_FIELD_STATES,
        help="Porcentaje aplicado para la retención sobre la base imponible del documento.",
    )

    journal_retention_id = fields.Many2one(
        comodel_name="account.journal",
        string="Diario Contable",
        tracking=True,
        help="Seleccione el diario contable que se utilizará para registrar la retención.",
        domain="[('company_id', '=?', company_id)]",
        states=READONLY_FIELD_STATES,
    )

    account_retention_id = fields.Many2one(
        comodel_name="account.account",
        string="Cuenta Contable",
        help="Cuenta contable utilizada para registrar la retención.",
        tracking=True,
        domain="[('company_id', '=?', company_id)]",
        states=READONLY_FIELD_STATES,
    )

    document_type_retention_id = fields.Many2one(
        comodel_name="l10n_latam.document.type",
        string="Tipo de Documento",
        readonly=False,
        auto_join=True,
        tracking=True,
        store=True,
        states=READONLY_FIELD_STATES,
        help="Tipo de documento utilizado para la retención.",
    )

    amount_minimum_retention = fields.Float(
        string="Monto Mínimo de Retención",
        store=True,
        tracking=True,
        states=READONLY_FIELD_STATES,
        help="Monto mínimo requerido para aplicar la retención.",
    )

    retention_series = fields.Char(
        string="Serie",
        related="journal_retention_id.code",
        readonly=True,
        help="Serie del documento utilizada en la numeración de comprobantes, como '001'.",
    )

    retention_sequence = fields.Char(
        string="Secuencia",
        related="journal_retention_id.retention_sequence",
        size=8,
        readonly=True,
        help="Número de secuencia del documento, con un tamaño máximo de 8 caracteres, como '00000001'.",
    )

    next_retention_sequence = fields.Char(
        string="Secuencia de Retención",
        size=8,
        store=True,
        default="00000001",
        states=READONLY_FIELD_STATES,
        help="Número de secuencia asignado automáticamente para la próxima retención.",
    )

    # ---------------------------------------------------------------------------- #
    #                               TODO - CONSTANTE                               #
    # ---------------------------------------------------------------------------- #
    PERCENTAGE_FACTOR = 100.0  # Constante para el cálculo de porcentajes

    # ---------------------------------------------------------------------------- #
    #                            TODO - METODO ONCHANGE                            #
    # ---------------------------------------------------------------------------- #
    @api.onchange("amount_base")
    def onchange_amount(self):
        if self.amount_base != self._origin.amount_base:
            self.amount = self.amount_base - self.amount_retention

    @api.onchange("is_retention_agent")
    def _onchange_is_retention_agent(self):
        """
        Restablece el campo 'has_retention' a False cuando el socio no es un agente de retención.
        Esto asegura que no se aplique retención si el socio no es un agente autorizado.
        """
        if not self.is_retention_agent:
            self.has_retention = False

    @api.onchange("retention_sequence")
    def _onchange_next_retention_sequence(self):
        """
        Calcula la próxima secuencia de retención sumando 1 al campo 'retention_sequence'.
        Asegura que la secuencia sea siempre de 8 dígitos, rellenando con ceros a la izquierda si es necesario.
        """
        if self.retention_sequence:
            try:
                # Asegurarse de que la secuencia actual es numérica
                current_sequence_int = int(self.retention_sequence)
                # Incrementar la secuencia
                next_sequence_int = current_sequence_int + 1
                # Formatear la próxima secuencia con 8 dígitos
                self.next_retention_sequence = str(next_sequence_int).zfill(8)
            except ValueError:
                # Si la secuencia actual no es un número válido, inicializar a '00000001'
                self.next_retention_sequence = "00000001"
        else:
            # Si no hay secuencia previa, inicializar a '00000001'
            self.next_retention_sequence = "00000001"

    @api.onchange("has_retention")
    def _onchange_retention_fields(self):
        """
        Actualiza los campos relacionados con la retención cuando cambia 'has_retention'.
        Si no se cumplen las condiciones (agente de retención, retención activa, y compañía válida),
        los campos se restablecen a sus valores por defecto.
        """
        # Verificar si el socio es agente de retención, si hay retención y si hay una compañía definida
        if self.is_retention_agent and self.has_retention and self.company_id:
            # Actualizar los campos relacionados con la retención según los valores de la compañía
            self.journal_retention_id = self.company_id.journal_retention_id
            self.account_retention_id = self.company_id.account_retention_id
            self.document_type_retention_id = self.company_id.document_type_retention_id
            self.percentage_retention = self.company_id.percentage_retention
            self.amount_minimum_retention = self.company_id.amount_minimum_retention
        else:
            # Restablecer los campos relacionados con la retención a sus valores por defecto
            self.journal_retention_id = False
            self.account_retention_id = False
            self.document_type_retention_id = False
            self.percentage_retention = 0.0
            self.amount_minimum_retention = 0.0

    # ---------------------------------------------------------------------------- #
    #                                TODO - METODOS                                #
    # ---------------------------------------------------------------------------- #
    def _calculate_amount_rt(self, percentage, amount_base):
        """
        Calcula el monto de retención basado en el monto y el porcentaje proporcionados.
        :param percentage: Porcentaje de retención.
        :param amount: Monto sobre el cual se calcula la retención.
        :return: Monto de retención calculado.
        """
        if amount_base < 0:
            raise UserError("El monto no puede ser negativo.")
        return (percentage * amount_base) / self.PERCENTAGE_FACTOR

    # ---------------------------------------------------------------------------- #
    #                             TODO - METODO COMPUTE                            #
    # ---------------------------------------------------------------------------- #
    # Método para calcular el monto base sujeto a retención
    @api.depends("has_retention", "amount_base", "percentage_retention")
    def _compute_amount_retention(self):
        """
        Calcula la base retenida multiplicando el monto total por el porcentaje de retención.
        Si no se ha definido un porcentaje de retención o el monto es cero, la base retenida será 0.
        """
        for record in self:
            if record.is_retention_agent and record.has_retention:
                # Verificar que el porcentaje de retención y el monto sean válidos
                if record.percentage_retention > 0 and record.amount_base > 0:
                    # Calcular la base retenida utilizando un método separado para mayor flexibilidad
                    record.amount_retention = self._calculate_amount_rt(
                        record.percentage_retention, record.amount_base
                    )
                else:
                    record.amount_retention = 0.0
            else:
                record.amount_retention = 0.0

    @api.depends("partner_id")
    def _compute_is_retention_agent(self):
        """
        Calcula si el socio es un agente de retención en función del campo `partner_id`.
        Solo actualiza el campo `is_retention_agent` si el estado no es 'posted'.
        """
        for record in self:
            if record.state not in ["posted", "cancel"]:
                if record.partner_id.is_retention_agent:
                    record.is_retention_agent = True
                else:
                    record.is_retention_agent = False

    # ---------------------------------------------------------------------------- #
    #                             TODO - BUTTON METODO                             #
    # ---------------------------------------------------------------------------- #
    def action_post(self):
        """
        Publica el pago y crea un asiento contable para la retención, si aplica.
        """
        # Llamar al método original `action_post` de la superclase
        payment_vals = super(AccountPayment, self).action_post()

        for record in self:
            # Verificar si el socio es un agente de retención y si hay retención
            if record.is_retention_agent and record.has_retention:
                # Validar que se han configurado correctamente los valores de la compañía
                if not all(
                    [
                        record.journal_retention_id,
                        record.account_retention_id,
                        record.document_type_retention_id,
                        record.percentage_retention is not None,
                        record.amount_minimum_retention is not None,
                    ]
                ):
                    raise ValidationError(
                        _(
                            "La configuración de retenciones está incompleta para la compañía: asegúrese de que el diario, la cuenta, el tipo de documento, el porcentaje y el monto mínimo de retención estén correctamente configurados."
                        )
                    )

                # Construir la secuencia de retención
                if record.retention_series:
                    retention_sequence = f"-{record.next_retention_sequence}"
                else:
                    retention_sequence = f"001-{record.next_retention_sequence}"

                if not record.retention_id:
                    try:
                        # Crear el registro de retención
                        account_retention_record = self.env["account.retention"].create(
                            {
                                "company_id": record.company_id.id,
                                "partner_id": record.partner_id.id,
                                "journal_id": record.journal_retention_id.id,
                                "account_id": record.account_retention_id.id,
                                "document_type_id": record.document_type_retention_id.id,
                                "document_number": retention_sequence,
                                "date_voucher": record.date,
                                "date_retention": record.date,
                                "percentage_retention": record.percentage_retention,
                                "amount_minimum_retention": record.amount_minimum_retention,
                                "state": "draft",
                            }
                        )

                        # Buscar la factura de proveedor relacionado con el pago
                        move_id = self.env["account.move"].search(
                            [
                                ("move_type", "=", "in_invoice"),
                                "|",
                                ("name", "=", record.ref),
                                ("ref", "=", record.ref),
                            ],
                            limit=1,
                        )

                        # Verificar que se haya creado el registro de retención y que exista la factura de proveedor
                        if account_retention_record and move_id.exists():
                            # Preparar la línea de retención
                            retention_line_data = {
                                "retention_id": account_retention_record.id,
                                "invoice_id": move_id.id,
                                "amount": record.amount_base,
                            }

                            # Crear la línea de retención
                            self.env["account.retention.line"].create(
                                [retention_line_data]
                            )

                            # Asegurarse de que se pueda ejecutar set_terminate solo si es un recordset válido
                            account_retention_record.set_terminate()

                            # Asignar el ID del registro de retención al campo correspondiente
                            record.retention_id = account_retention_record.id
                        else:
                            raise ValidationError(
                                _(
                                    "No se pudo crear el registro de retención debido a que falta un comprobante relacionado."
                                )
                            )
                    except Exception as e:
                        # Manejar cualquier error durante la creación del registro de retención
                        raise UserError(
                            _("No se pudo crear el registro de retención. Error: %s")
                            % str(e)
                        )
        return payment_vals

    def open_related_account_retention(self):
        """Abre la vista del formulario del comprobante de retención relacionado."""
        if not self.retention_id:
            raise UserError(_("No hay un comprobante de retención relacionado."))

        action = {
            "type": "ir.actions.act_window",
            "name": _("Comprobante de Retención"),
            "res_model": "account.retention",
            "view_mode": "form",
            "res_id": self.retention_id.id,  # Especifica el ID del registro a abrir
            "view_id": False,  # Agregar el id si se desea una vista sspecífica
            "target": "current",
            "context": self.env.context,
        }
        return action
