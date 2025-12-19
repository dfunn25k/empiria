from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError

READONLY_FIELD_STATES = {
    state: [("readonly", True)] for state in {"terminate", "cancel"}
}


class AccountRetention(models.Model):
    _inherit = "account.retention"

    # ---------------------------------------------------------------------------- #
    #                             TODO - CAMPOS DEFAULT                            #
    # ---------------------------------------------------------------------------- #
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Compañía",
        default=lambda self: self.env.company,
        readonly=True,
        index=True,
        help="Compañía a la que pertenece este registro.",
    )

    # ---------------------------------------------------------------------------- #
    #                    TODO - CAMPOS COMPROBANTE DE RETENCION                    #
    # ---------------------------------------------------------------------------- #
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Proveedor",
        required=True,
        tracking=True,
        domain="[('company_id', 'in', [company_id, False]), ('is_retention_agent', '=', True)]",
        help="Proveedor asociado a la retención.",
        states=READONLY_FIELD_STATES,
    )

    journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Diario Contable",
        required=True,
        tracking=True,
        help="Seleccione el diario contable que se utilizará para registrar la retención.",
        domain="[('company_id', '=?', company_id)]",
        states=READONLY_FIELD_STATES,
    )

    retention_series = fields.Char(
        string="Serie",
        related="journal_id.code",
        readonly=False,
        help="Serie del documento utilizada en la numeración de comprobantes, como '001'.",
    )

    retention_sequence = fields.Char(
        string="Secuencia",
        related="journal_id.retention_sequence",
        size=8,
        readonly=False,
        help="Número de secuencia del documento, con un tamaño máximo de 8 caracteres, como '00000001'.",
    )

    account_id = fields.Many2one(
        comodel_name="account.account",
        string="Cuenta Contable",
        required=True,
        tracking=True,
        help="Cuenta contable utilizada para registrar la retención.",
        domain="[('company_id', '=?', company_id)]",
        states=READONLY_FIELD_STATES,
    )

    document_type_id = fields.Many2one(
        comodel_name="l10n_latam.document.type",
        string="Tipo de Documento",
        required=True,
        tracking=True,
        auto_join=True,
        store=True,
        states=READONLY_FIELD_STATES,
        help="Tipo de documento utilizado para la retención.",
    )

    document_number = fields.Char(
        string="Número de Documento",
        compute="_compute_document_number",
        inverse="_inverse_document_number",
        size=64,
        required=True,
        readonly=False,
        store=True,
        states=READONLY_FIELD_STATES,
        help="Número único de identificación del documento para efectos de retención.",
    )

    date_voucher = fields.Date(
        string="Fecha del Comprobante",
        default=fields.Date.context_today,
        required=True,
        tracking=True,
        states=READONLY_FIELD_STATES,
        help="Fecha de emisión del comprobante. Se utiliza la fecha actual por defecto.",
    )

    date_retention = fields.Date(
        string="Fecha Contable",
        default=fields.Date.context_today,
        required=True,
        tracking=True,
        states=READONLY_FIELD_STATES,
        help="Fecha contable de la retención. Se utiliza la fecha actual por defecto.",
    )

    # ---------------------------------------------------------------------------- #
    #                            TODO - CAMPO INFO TASA                            #
    # ---------------------------------------------------------------------------- #
    percentage_retention = fields.Float(
        string="% Retención",
        store=True,
        tracking=True,
        required=True,
        states=READONLY_FIELD_STATES,
        help="Porcentaje aplicado para la retención.",
    )

    amount_minimum_retention = fields.Float(
        string="Monto Mínimo de Retención",
        store=True,
        tracking=True,
        required=True,
        states=READONLY_FIELD_STATES,
        help="Monto mínimo requerido para aplicar la retención.",
    )

    inverse_company_rate = fields.Float(
        string="Tasa de Cambio Inversa",
        digits=("Product Price", 6),
        default=1.000,
        required=True,
        store=True,
        readonly=False,
        precompute=True,
        states=READONLY_FIELD_STATES,
        help="Tasa de cambio utilizada para la conversión.",
    )

    # ---------------------------------------------------------------------------- #
    #                            TODO - CAMPOS CONEXION                            #
    # ---------------------------------------------------------------------------- #
    account_move_id = fields.Many2one(
        comodel_name="account.move",
        string="Asiento Contable Relacionado",
        ondelete="restrict",
        index=True,
        help="Selecciona el asiento contable relacionado con este registro.",
    )

    # ---------------------------------------------------------------------------- #
    #                              TODO - CAMPOS OTROS                             #
    # ---------------------------------------------------------------------------- #
    note = fields.Text(
        string="Observaciones",
        help="Notas y observaciones adicionales relacionadas con la retención.",
    )

    # ---------------------------------------------------------------------------- #
    #                               TODO - CONSTANTE                               #
    # ---------------------------------------------------------------------------- #
    # Número de dígitos para la secuencia
    DIGITS = 8

    # ---------------------------------------------------------------------------- #
    #                            TODO - METODO ONCHANGE                            #
    # ---------------------------------------------------------------------------- #
    @api.onchange("company_id")
    def _onchange_company_id(self):
        """
        Actualiza los campos relacionados con la compañía cuando ésta cambia. Si se selecciona una nueva compañía,
        se establecen los valores correspondientes de retención; en caso contrario, los campos se limpian.
        """
        if self.company_id:
            # Verificar si la compañía ha cambiado para actualizar los campos
            if self._origin.company_id != self.company_id:
                # Actualizar los campos de retención según la compañía seleccionada
                self.journal_id = self.company_id.journal_retention_id
                self.account_id = self.company_id.account_retention_id
                self.document_type_id = self.company_id.document_type_retention_id
                self.percentage_retention = self.company_id.percentage_retention
                self.amount_minimum_retention = self.company_id.amount_minimum_retention
        else:
            # Limpiar los campos si no hay una compañía seleccionada
            self.journal_id = False
            self.account_id = False
            self.document_type_id = False
            self.percentage_retention = 0.0
            self.amount_minimum_retention = 0.0

    @api.onchange("journal_id")
    def _onchange_journal_id(self):
        """
        Limpia el número de documento cuando se cambia el diario seleccionado.
        Esto ayuda a evitar inconsistencias de datos en casos donde el diario se modifica
        después de haber asignado un número de documento.
        """
        if self.journal_id:
            # Limpiar 'document_number' solo si el diario ha cambiado
            if self._origin.journal_id != self.journal_id:
                self.document_number = False
        else:
            # Si no hay diario seleccionado, limpiar 'document_number' por defecto
            self.document_number = False

    @api.onchange("date_retention")
    def _onchange_date_retention(self):
        """
        Método que se ejecuta al cambiar la fecha de retención.
        Calcula la tasa de cambio inversa de la compañía según la nueva fecha de retención.
        Si no se encuentran tasas de cambio para la fecha, se establece la tasa inversa a 1.
        """
        if self.date_retention and self.date_retention != self._origin.date_retention:
            # Obtener las tasas de cambio en USD para la fecha especificada
            usd_rates = self.get_usd_currency_rates()

            # Si existen tasas de cambio, calcular la tasa inversa; de lo contrario, establecer a 1
            if usd_rates:
                inverse_rate = self._get_inverse_company_rate(
                    usd_rates, self.date_retention
                )
                # Asignar la tasa inversa o 1 si no se encuentra
                self.inverse_company_rate = inverse_rate or 1.0
            else:
                # Si no hay tasas de cambio disponibles, establecer la tasa inversa por defecto a 1
                self.inverse_company_rate = 1.0

    # ---------------------------------------------------------------------------- #
    #                                TODO - METODOS                                #
    # ---------------------------------------------------------------------------- #
    def split_string_by_hyphen(self, value, digits):
        """
        Divide una cadena en dos partes usando el primer guion encontrado.
        Valida que la parte después del guion sea numérica y tenga una longitud mínima.

        Args:
            value (str): Cadena a dividir que debe contener al menos un guion '-'.
            digits (int): Número mínimo de dígitos para la parte después del guion.

        Returns:
            tuple: Contiene dos cadenas, la primera parte antes del guion y la segunda después del guion, con el formato aplicado.
        """
        # Verificación inicial del valor y el tipo de datos
        if not isinstance(value, str) or not value:
            raise ValidationError("El valor debe ser una cadena de texto no vacía.")

        # Intentar dividir la cadena en dos partes usando el primer guion
        parts = value.split("-", 1)

        if len(parts) < 2:
            raise ValidationError(
                "El campo Número de Documento debe contener al menos un guion '-'."
            )

        # Extraer las partes antes y después del guion y remover espacios en blanco
        before_hyphen = parts[0].strip()
        after_hyphen = parts[1].strip()

        # Validar que la segunda parte sea numérica y ajustarla al número mínimo de dígitos
        if not after_hyphen.isdigit():
            raise ValidationError("La parte después del guion debe ser numérica.")

        # Asegurar que el número resultante cumpla con el mínimo de dígitos especificado
        after_hyphen = after_hyphen.zfill(digits)

        return before_hyphen, after_hyphen

    def _generate_correlative_name(self, prefix, series, sequence, digits):
        """
        Genera un nombre correlativo basado en un prefijo, una serie y una secuencia numérica,
        donde la secuencia se formatea a la izquierda con ceros para cumplir con el número de dígitos especificado.

        Args:
            prefix (str)   : Prefijo opcional para el nombre (por ejemplo, 'R'). Por defecto, es una cadena vacía.
            series (str)   : Serie del documento (por ejemplo, '001'). Por defecto, es una cadena vacía.
            sequence (str) : Secuencia numérica que debe formatearse con ceros a la izquierda.
            digits (int)   : Número mínimo de dígitos para la secuencia. Si es 0, no se formateará.

        Returns:
            str: Nombre correlativo formateado en el formato 'prefixseries-sequence' o 'prefixseries' si no hay secuencia.

        Ejemplo:
            'R001-00000001'
        """
        # Validar los parámetros de entrada
        if not prefix or not series or not sequence.isdigit():
            raise ValidationError(
                "El prefijo, la serie y la secuencia deben ser válidos y no estar vacíos."
            )

        # Formatear la secuencia con ceros a la izquierda según el número de dígitos especificado
        formatted_sequence = str(int(sequence)).zfill(digits)

        # Construir y retornar el nombre correlativo en el formato especificado
        return f"{prefix}{series}-{formatted_sequence}"

    def _get_next_document_number(self, correlative_prefix, digits):
        """
        Genera el siguiente número de documento basado en el prefijo correlativo y la cantidad de dígitos especificada.

        Args:
            correlative_prefix (str): Prefijo utilizado en la búsqueda del último número de documento.
            digits (int)            : Número de dígitos que debe tener la secuencia del documento.

        Returns:
            str: El siguiente número de documento en la secuencia formateado con ceros a la izquierda.

        Ejemplo:
            Si el último número es '00000001' y digits=8, retornará '00000002'.
        """
        try:
            # Inicializa el número siguiente predeterminado con ceros según el número de dígitos
            next_number = str(1).zfill(digits)

            # Buscar el último documento que coincida con el prefijo correlativo, excluyendo el documento actual
            last_document = self.search(
                [
                    ("name", "like", f"{correlative_prefix[-digits:]}%"),
                    ("id", "!=", self._origin.id),
                ],
                limit=1,
                order="name DESC",
            )

            # Si se encuentra un último documento, extraer y procesar su secuencia
            if last_document:
                last_sequence = last_document.name[-digits:]
                if last_sequence.isdigit():
                    # Incrementa el número secuencial y formatea con ceros
                    next_number = str(int(last_sequence) + 1).zfill(digits)
            else:
                # Si no se encuentra un documento previo, extraer la secuencia del prefijo
                if correlative_prefix[-digits:].isdigit():
                    initial_sequence = correlative_prefix[-digits:]
                    next_number = str(int(initial_sequence)).zfill(digits)

            return next_number

        except Exception as e:
            # Manejar cualquier excepción y levantar un error con un mensaje detallado
            raise UserError(
                _("Error al generar el siguiente número de documento: %s") % str(e)
            )

    # ---------------------------------------------------------------------------- #
    #                             TODO - MÉTODO COMPUTE                            #
    # ---------------------------------------------------------------------------- #
    @api.depends("name")
    def _compute_document_number(self):
        """
        Calcula el número de documento eliminando el prefijo del campo 'name' si existe.
        Si el prefijo no está presente o el campo 'name' está vacío, el número de documento se establece en False.
        """
        for record in self.filtered(lambda r: r.name and r.name != "/"):
            # Obtener el prefijo del tipo de documento relacionado o una cadena vacía si no existe
            prefijo = record.document_type_id.doc_code_prefix or ""

            # Verificar si el nombre comienza con el prefijo y establecer el número de documento en consecuencia
            if prefijo and record.name.startswith(prefijo):
                record.document_number = record.name[len(prefijo) :].strip()
            else:
                record.document_number = False

    # ---------------------------------------------------------------------------- #
    #                             TODO - METODO INVERSE                            #
    # ---------------------------------------------------------------------------- #
    @api.onchange("document_number")
    def _inverse_document_number(self):
        """
        Actualiza el campo 'name' en función del prefijo, serie y secuencia del documento,
        considerando el tipo de documento y el sufijo del diario.
        """
        for rec in self.filtered("document_type_id"):
            # Inicialización de valores de prefijo, serie, y secuencia
            document_number = rec.document_number or ""
            prefix = rec.document_type_id.doc_code_prefix or ""
            series = rec.retention_series or ""
            sequence = rec.retention_sequence or ""
            digits = self.DIGITS

            # Si no hay un prefijo definido, asigna un valor predeterminado a 'name'
            if not prefix:
                rec.name = "/"
                continue

            # CASO 1: Si no hay serie y es la primera secuencia, inicializa el correlativo, extrae los componentes del número de documento
            if not series and (sequence == str(1).zfill(digits) or not sequence):
                rec.name = "/"
                if document_number:
                    # Descomponer el número de documento en parte antes y después del guion
                    before_hyphen, after_hyphen = self.split_string_by_hyphen(
                        document_number, digits
                    )
                    # Generar el nombre correlativo basado en prefijo, serie y secuencia
                    rec.name = self._generate_correlative_name(
                        prefix, before_hyphen, after_hyphen, digits
                    )

                    # Actualizar la serie y la secuencia con las partes obtenidas
                    rec.retention_series = before_hyphen
                    rec.retention_sequence = after_hyphen

            # CASO 2: Si no hay secuencia o es la primera secuencia, establece una secuencia por defecto
            elif sequence == str(1).zfill(digits) or not sequence:
                rec.name = "/"
                if document_number:
                    # Dividir el número de documento en serie y secuencia
                    before_hyphen, after_hyphen = self.split_string_by_hyphen(
                        document_number, digits
                    )
                    # Generar el nombre correlativo basado en prefijo, serie y secuencia
                    rec.name = self._generate_correlative_name(
                        prefix, series, after_hyphen, digits
                    )

                    rec.retention_sequence = after_hyphen

            # CASO 3: Si 'name' ya tiene un valor, verifica y actualiza el número correlativo
            elif rec.name != "/":
                # Dividir el número de documento en la parte anterior y posterior al guion
                series_part, sequence_part = self.split_string_by_hyphen(
                    document_number, digits
                )
                # Generar el nombre correlativo utilizando el prefijo, la serie y la secuencia extraída
                correlative_name = self._generate_correlative_name(
                    prefix, series_part, sequence_part, digits
                )

                # Comprobar si existe un comprobante con el mismo nombre
                if self.search(
                    [
                        ("name", "like", correlative_name),
                        ("id", "!=", rec._origin.id),
                    ]
                ):
                    raise UserError(
                        _(
                            "Se encontró un comprobante de retención con el número correlativo '{correlative_name}'. "
                            "Revise la numeración para evitar duplicados."
                        ).format(correlative_name=correlative_name)
                    )
                # Asignar el nuevo nombre generado al campo 'name'
                rec.name = correlative_name

            # CASO 4: Si se genera un nuevo registro, asigna el ultima secuencia correlativo
            else:
                rec.name = "/"

                # Buscar el último documento que coincida con el prefijo y la serie en el nombre
                last_document = self.search(
                    [
                        ("name", "like", f"{prefix}{series}-%"),
                        ("id", "!=", self._origin.id),
                    ],
                    limit=1,
                    order="name DESC",
                )

                # Extraer la secuencia numérica del nombre del documento encontrado, si existe
                if last_document:
                    sequence = last_document.name[-digits:]

                # Generar el patrón correlativo basado en el prefijo, la serie y la secuencia
                correlative_pattern = self._generate_correlative_name(
                    prefix, series, sequence, digits
                )

                # Obtener el siguiente número de documento en la secuencia
                next_document_number = self._get_next_document_number(
                    correlative_pattern, digits
                )

                # Asignar el nuevo nombre generado al campo 'name'
                rec.name = self._generate_correlative_name(
                    prefix, series, next_document_number, digits
                )

                # Extraer serie y secuencia del name generado para asignarlos a los campos correspondientes
                if rec.name.startswith(prefix):
                    # Dividir la cadena para obtener la serie y la secuencia
                    extracted_series, extracted_sequence = self.split_string_by_hyphen(
                        rec.name[len(prefix) :], digits
                    )
                    # Asignar los valores extraídos a los campos correspondientes
                    rec.retention_series = extracted_series
                    rec.retention_sequence = extracted_sequence
